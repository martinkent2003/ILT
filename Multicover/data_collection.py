import os
import csv
import sys
import re
import unicodedata
from pathlib import Path
from typing import List

N5_KANJI_STR = ("人一日大年出本中子見国上分生行二間時気十女三前入小後長下学月何来話山高今書五名金男外四先川東聞語九食八水天木六万白七円電父北車母半百土西読千校右南左友火毎雨休午")
N5_KANJI = set(N5_KANJI_STR)

CSV_PATH = Path("materials.csv")
CSV_HEADER = ["Name", "Cost", "Kanji"]


def ensure_csv_header(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)


def normalize_text(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def read_multiline(prompt: str = "Paste text (finish with a single line 'END'):\n") -> str:
    print(prompt, end="")
    lines: List[str] = []
    while True:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            print("\nInterrupted. Returning to name prompt.")
            return ""
        if line == "":
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "".join(lines)


def split_paragraphs(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip()
    if not text:
        return []
    parts = re.split(r"\n\s*\n+", text)
    paras = [p.strip() for p in parts if p.strip()]
    return paras


def extract_n5_kanji(paragraph: str) -> str:
    seen = set()
    ordered = []
    for ch in paragraph:
        if ch in N5_KANJI and ch not in seen:
            seen.add(ch)
            ordered.append(ch)
    return "".join(ordered)


def main():
    ensure_csv_header(CSV_PATH)

    while True:
        try:
            name = input("Excerpt name (or 'q' to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if name.lower() == "q":
            break

        raw = read_multiline()
        raw = normalize_text(raw)

        paragraphs = split_paragraphs(raw)
        if not paragraphs:
            print("No paragraphs detected. Skipping.\n")
            continue

        rows = []
        for idx, para in enumerate(paragraphs, start=1):
            kanji_concat = extract_n5_kanji(para)

            # ---- NEW CONDITION: skip if no N5 kanji ----
            if not kanji_concat:
                continue

            material_name = f"{name} {idx}"
            cost = len(para)
            rows.append([material_name, str(cost), kanji_concat])

        if not rows:
            print("No paragraphs contained N5 kanji. Nothing added.\n")
            continue

        with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"Appended {len(rows)} rows to {CSV_PATH.resolve()}\n")


if __name__ == "__main__":
    main()
