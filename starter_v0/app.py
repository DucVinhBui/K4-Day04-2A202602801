from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDERS = ("openrouter", "openai", "anthropic", "gemini")


def new_transcript(
    *, provider: str, model: str | None, version: str, history_window: int, max_tool_rounds: int
) -> tuple[dict[str, Any], Path, dict[str, str]]:
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join((safe_slug(version), safe_slug(provider), "ui", timestamp))
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    data: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return data, path, artifact_version_dict(artifact)


def render_trace(turn: dict[str, Any]) -> None:
    with st.expander("Tool trace", expanded=bool(turn.get("tool_events"))):
        if not turn.get("rounds"):
            st.caption("No tool was called in this turn.")
            return
        for round_record in turn["rounds"]:
            st.markdown(f"**Round {round_record['round']}**")
            if round_record.get("assistant_text"):
                st.caption(round_record["assistant_text"])
            calls = round_record.get("tool_calls") or []
            results = round_record.get("tool_results") or []
            if not calls:
                st.code("No tool call", language="text")
            for index, call in enumerate(calls):
                st.code(
                    f"{call['name']}({json.dumps(call.get('args', {}), ensure_ascii=False)})",
                    language="text",
                )
                if index < len(results):
                    result = results[index].get("result")
                    is_error = isinstance(result, dict) and bool(result.get("error"))
                    (st.error if is_error else st.success)(
                        json.dumps(result, ensure_ascii=False, indent=2, default=str)
                    )


def reset_chat(config: tuple[Any, ...]) -> None:
    provider_name, model, version, history_window, max_tool_rounds = config
    transcript, path, artifact = new_transcript(
        provider=provider_name,
        model=model or None,
        version=version,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    st.session_state.chat_config = config
    st.session_state.history = []
    st.session_state.transcript = transcript
    st.session_state.transcript_path = path
    st.session_state.artifact = artifact


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🛠️", layout="wide")
    st.title("🛠️ IT Helpdesk Agent")
    st.caption("Live chat with auditable tool calls and local transcript logging")

    with st.sidebar:
        st.header("Run configuration")
        provider_name = st.selectbox("Provider", PROVIDERS)
        model = st.text_input("Model override", placeholder="Use provider default")
        version = st.text_input("Artifact version", value="v4")
        history_window = st.number_input("History window", min_value=1, max_value=20, value=5)
        max_tool_rounds = st.number_input("Maximum tool rounds", min_value=1, max_value=10, value=4)
        config = (provider_name, model.strip(), version.strip() or "v4", history_window, max_tool_rounds)
        if "chat_config" not in st.session_state or st.session_state.chat_config != config:
            reset_chat(config)
        if st.button("New conversation", use_container_width=True):
            reset_chat(config)
            st.rerun()

        artifact = st.session_state.artifact
        st.subheader("Artifact identity")
        st.code(artifact["artifact_version"], language="text")
        st.caption(f"Prompt SHA-256: {artifact['prompt_hash']}")
        st.caption(f"Tools SHA-256: {artifact['tools_hash']}")
        st.subheader("Transcript")
        st.code(str(st.session_state.transcript_path), language="text")

    for turn in st.session_state.transcript["turns"]:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("status") == "provider_error":
                st.error(turn.get("error", "Unknown provider error"))
            else:
                st.markdown(turn.get("assistant_text") or "")
            render_trace(turn)

    user_text = st.chat_input("Describe the IT issue or request…")
    if not user_text:
        return

    with st.chat_message("user"):
        st.markdown(user_text)

    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    with st.chat_message("assistant"):
        try:
            prompt_path = ARTIFACTS_DIR / "system_prompt.md"
            tools_path = ARTIFACTS_DIR / "tools.yaml"
            system_prompt = prompt_path.read_text(encoding="utf-8")
            tools = to_openai_tools(load_tool_declarations(tools_path))
            provider = make_provider(provider_name)
            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(st.session_state.history, int(history_window)),
                {"role": "user", "content": user_text},
            ]
            with st.spinner("Agent is working…"):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=model.strip() or None,
                    max_tool_rounds=int(max_tool_rounds),
                )
            turn.update(result)
            st.markdown(result["assistant_text"])
            render_trace(turn)
            st.session_state.history.extend(
                (
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": result["assistant_text"]},
                )
            )
        except Exception as exc:
            turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}")
            st.error(turn["error"])

    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


if __name__ == "__main__":
    main()
