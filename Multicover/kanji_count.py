import csv
from pathlib import Path
from collections import Counter
import unicodedata

N5_KANJI_STR = ("人一日大年出本中子見国上分生行二間時気十女三前入小後長下学月何来話山高今書五名金男外四先川東聞語九食八水天木六万白七円電父北車母半百土西読千校右南左友火毎雨休午")
N5_KANJI = set(N5_KANJI_STR)

CSV_PATH = Path("materials.csv")

def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    counter = Counter()

    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kanji_str = unicodedata.normalize("NFC", row["Kanji"])
            for ch in kanji_str:
                if ch in N5_KANJI:
                    counter[ch] += 1

    missing_kanji = [k for k in N5_KANJI if counter[k] == 0]
    missing_kanji_sorted = sorted(missing_kanji)

    print("\nN5 Kanji Frequency Report\n")

    print("Kanji that don't appear:", "、".join(missing_kanji_sorted))
    print("Number of kanji that don't appear:", len(missing_kanji_sorted))
    print()

    sorted_items = sorted(counter.items(), key=lambda x: x[1])
    for kanji, freq in sorted_items:
        print(f"{kanji} : {freq}")

    print("\nTotal kanji appearances:", sum(counter.values()))
    print("Number of unique N5 kanji encountered:", len(counter))


if __name__ == "__main__":
    main()
