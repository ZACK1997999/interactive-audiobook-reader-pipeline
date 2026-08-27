import json

with open('/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch37_canonical_sentences.json') as f:
    can = json.load(f)

with open('/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch37_full_analysis.json') as f:
    existing = json.load(f)

full = []
for c, e in zip(can, existing):
    entry = {
        "id": c["id"],
        "elem_idx": c["elem_idx"],
        "tag": c["tag"],
        "text": c["text"],
        "is_heading": c["is_heading"],
        "trans": e["trans"],
        "vocab": e["vocab"]
    }
    full.append(entry)

with open('/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch37_full_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(full, f, indent=2, ensure_ascii=False)

print(f"Updated ch37 with {len(full)} items.")
