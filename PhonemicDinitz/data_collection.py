import pandas as pd
import numpy as np
from collections import defaultdict
import networkx as nx
from typing import List, Dict, Tuple, Set
import panphon

feature_table = panphon.FeatureTable()

# Load Phoible database for phoneme inventories
# Download from: https://github.com/phoible/dev
phoible_df = pd.read_csv('phoible.csv')

def get_language_phoneme_inventory(language_name: str, debug=False) -> List[str]:
    """
    Extract phoneme inventory for a specific language from Phoible
    """
    language_data = phoible_df[phoible_df['LanguageName'] == language_name]

    if debug:
        print(f"\nDebug info for {language_name}:")
        print(f"Total rows: {len(language_data)}")
        print(f"Unique inventory IDs: {language_data['InventoryID'].nunique()}")
        print(f"Sources: {language_data['Source'].unique()}")
        print("\nInventory breakdown:")
        for inv_id in language_data['InventoryID'].unique():
            inv_data = language_data[language_data['InventoryID'] == inv_id]
            source = inv_data['Source'].iloc[0]
            print(f"  Inventory {inv_id} ({source}): {len(inv_data)} phonemes")

    # Get unique phonemes (may have multiple inventories per language)
    phonemes = language_data['Phoneme'].unique().tolist()

    # Clean up (remove tone marks, length markers for initial model)
    cleaned_phonemes = []
    for p in phonemes:
        # Remove suprasegmentals for simplified model
        if p not in ['ː', '˥', '˦', '˧', '˨', '˩']:  # length, tones
            cleaned_phonemes.append(p)

    return cleaned_phonemes


def get_single_inventory(language_name: str, prefer_source: str = None) -> List[str]:
    """
    Get a single phoneme inventory for a language (not merged from multiple sources)

    Args:
        language_name: Name of the language
        prefer_source: Preferred source (e.g., 'upsid', 'spa', 'ph', 'gm', 'ra')
    """
    language_data = phoible_df[phoible_df['LanguageName'] == language_name]

    if len(language_data) == 0:
        return []

    # If preferred source specified, try to use it
    if prefer_source:
        source_data = language_data[language_data['Source'] == prefer_source]
        if len(source_data) > 0:
            language_data = source_data

    # Get the first inventory ID
    first_inventory = language_data['InventoryID'].iloc[0]
    inventory_data = language_data[language_data['InventoryID'] == first_inventory]

    phonemes = inventory_data['Phoneme'].unique().tolist()

    # Clean up
    cleaned_phonemes = []
    for p in phonemes:
        if p not in ['ː', '˥', '˦', '˧', '˨', '˩']:
            cleaned_phonemes.append(p)

    return cleaned_phonemes


if __name__ == "__main__":
    print("=" * 60)
    print("MERGED INVENTORIES (all sources combined)")
    print("=" * 60)

    # Get Japanese phoneme inventory (merged from all sources)
    japanese_phonemes = get_language_phoneme_inventory('Japanese', debug=True)
    print(f"\nNumber of Japanese phonemes (merged): {len(japanese_phonemes)}")
    print(f"Japanese phonemes: {japanese_phonemes}")

    # Get English phoneme inventory (merged from all sources)
    english_phonemes = get_language_phoneme_inventory('English', debug=True)
    print(f"\nNumber of English phonemes (merged): {len(english_phonemes)}")
    print(f"English phonemes: {english_phonemes}")

    print("\n" + "=" * 60)
    print("SINGLE INVENTORY (first inventory only)")
    print("=" * 60)

    # Get single inventory for Japanese
    japanese_single = get_single_inventory('Japanese')
    print(f"\nJapanese (single inventory): {len(japanese_single)} phonemes")
    print(f"Phonemes: {japanese_single}")

    # Get single inventory for English
    english_single = get_single_inventory('English')
    print(f"\nEnglish (single inventory): {len(english_single)} phonemes")
    print(f"Phonemes: {english_single}")
