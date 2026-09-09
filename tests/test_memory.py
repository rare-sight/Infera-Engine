import json

from core import memory


def test_save_and_load_run(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(memory, "MEMORY_DIR", str(tmp_path))
    path = memory.save_run(
        "A topic / with punctuation", {"analysis": "analysis", "research": "research"}
    )
    with open(path, encoding="utf-8") as saved_file:
        assert json.load(saved_file)["topic"] == "A topic / with punctuation"
    assert memory.load_run("A topic / with punctuation")["research"] == "research"


def test_list_saved_topics_ignores_invalid_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(memory, "MEMORY_DIR", str(tmp_path))
    (tmp_path / "valid.json").write_text('{"topic": "A valid topic"}', encoding="utf-8")
    (tmp_path / "invalid.json").write_text("not json", encoding="utf-8")
    assert memory.list_saved_topics() == ["A valid topic"]
