import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chat import (
    ARTIFACTS_DIR, now_iso,
    run_model_tool_loop, write_transcript
)
TRANSCRIPTS_DIR = ROOT / "transcripts"
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
openai_tools = to_openai_tools(declarations)
artifact_version = build_artifact_version("v0", ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")
provider = make_provider("openrouter")

questions = [
    "Tìm 2 bài báo khoa học mới nhất về Retrieval-Augmented Generation trên arXiv và tóm tắt ngắn gọn.",
    "Tìm tin tức công nghệ nổi bật về OpenAI trong tuần này.",
    'Loại bỏ các URL trùng lặp trong danh sách này: [{"url": "https://example.com/news?utm_source=chat"}, {"url": "https://example.com/news"}, {"url": "https://vinuni.edu.vn"}]'
]

TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

for i, q in enumerate(questions, 1):
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    t_id = f"v0_openrouter_ui_{timestamp}"
    t_path = TRANSCRIPTS_DIR / f"{t_id}.transcript.json"
    transcript = {
        "transcript_id": t_id,
        **artifact_version_dict(artifact_version),
        "provider": "openrouter",
        "model": "openai/gpt-4o-mini",
        "source": "streamlit",
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": q}
    ]
    turn_record = {
        "turn_index": 1,
        "started_at": now_iso(),
        "user": q,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        res = run_model_tool_loop(provider=provider, messages=messages, tools=openai_tools, model="openai/gpt-4o-mini", max_tool_rounds=3)
        turn_record.update(res)
    except Exception as e:
        turn_record.update({"status": "provider_error", "error": str(e)})
    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(t_path, transcript)
    print(f"Generated transcript {i}: {t_path.name}")
