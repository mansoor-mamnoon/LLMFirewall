from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from attackgen.mutate import MutateConfig, dedup_texts, mutate_payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def is_attack_seed(case: dict[str, Any]) -> bool:
    # keep only non-benign attacks
    if case.get("is_benign") is True:
        return False
    # must have payload text
    payload = case.get("payload", "")
    return isinstance(payload, str) and payload.strip() != ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help="Path to your existing dataset JSONL")
    ap.add_argument(
        "--out",
        default="data/attacks_mutated.jsonl",
        help="Output JSONL path (mutated attacks)",
    )
    ap.add_argument("--variants", type=int, default=10, help="Variants per seed attack")
    ap.add_argument("--seed", type=int, default=1337, help="RNG seed")
    ap.add_argument(
        "--dedup-threshold", type=float, default=0.92, help="Cosine threshold for dedup"
    )
    args = ap.parse_args()

    seeds_path = Path(args.seeds)
    out_path = Path(args.out)

    cfg = MutateConfig(
        variants_per_seed=args.variants,
        rng_seed=args.seed,
        dedup_cosine_threshold=args.dedup_threshold,
        embed_dim=512,
    )
    rng = random.Random(cfg.rng_seed)

    seeds = load_jsonl(seeds_path)
    attack_seeds = [c for c in seeds if is_attack_seed(c)]

    all_mutated_rows: list[dict[str, Any]] = []
    total_before = 0

    for c in attack_seeds:
        attack_id = str(c.get("attack_id", "X"))
        attack_type = str(c.get("attack_type", "direct"))
        payload = str(c.get("payload", ""))

        # generate candidates
        candidates: list[str] = []
        for _ in range(cfg.variants_per_seed):
            candidates.append(mutate_payload(payload, rng))

        # dedup within this seed
        total_before += len(candidates)
        unique_payloads = dedup_texts(
            candidates,
            dim=cfg.embed_dim,
            cosine_threshold=cfg.dedup_cosine_threshold,
        )

        # build mutated rows keeping the same schema as your eval expects
        for j, mp in enumerate(unique_payloads):
            new_id = f"{attack_id}_m{j:02d}"
            row = dict(c)
            row["attack_id"] = new_id
            row["attack_type"] = attack_type
            row["payload"] = mp
            row["is_benign"] = False
            # keep policy field if present
            if "policy" not in row:
                row["policy"] = {}
            all_mutated_rows.append(row)

    # global dedup across all mutated payloads (optional but helps keep 800–1500 target)
    all_payloads = [r["payload"] for r in all_mutated_rows]
    kept_payloads = set(
        dedup_texts(
            all_payloads,
            dim=cfg.embed_dim,
            cosine_threshold=cfg.dedup_cosine_threshold,
        )
    )
    final_rows = [r for r in all_mutated_rows if r["payload"] in kept_payloads]

    write_jsonl(out_path, final_rows)

    print("Seeds (attacks):", len(attack_seeds))
    print("Mutated candidates:", total_before)
    print("Mutated after per-seed dedup:", len(all_mutated_rows))
    print("Mutated after global dedup:", len(final_rows))
    print("Wrote:", str(out_path))


if __name__ == "__main__":
    main()
