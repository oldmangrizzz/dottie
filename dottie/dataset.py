"""Non-production synthetic curriculum file guards."""
import hashlib
import json
from pathlib import Path


def load_dataset(path):
    rows = []
    for index, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as ex:
                raise ValueError(f"Invalid JSONL line {index}: {ex}") from ex
    return rows


def dataset_integrity(train, evaluation):
    ids = [row["id"] for row in train + evaluation]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate sample ID across train/eval")
    prompts = [hashlib.sha256(row["scenario"].strip().lower().encode("utf-8")).hexdigest() for row in train + evaluation]
    if len(set(prompts)) != len(prompts):
        raise ValueError("Identical scenario appears in train/eval")
    for sample in train + evaluation:
        if sample.get("evidence_status") != "SYNTHETIC_UNREVIEWED" or sample.get("human_label_reviewed") is not False:
            raise ValueError("Corpus status improperly promoted to observed or reviewed")
        if not sample.get("source_doc") or not sample.get("hazards"):
            raise ValueError("Missing source or threat model mapping")
    return True
