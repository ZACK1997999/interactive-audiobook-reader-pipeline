import json

for ch in [35, 36, 37]:
    can_path = f'/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch{ch}_canonical_sentences.json'
    full_path = f'/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch{ch}_full_analysis.json'
    
    with open(can_path) as f:
        can = json.load(f)
    with open(full_path) as f:
        existing = json.load(f)
        
    assert len(can) == len(existing)
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
        
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(full, f, indent=2, ensure_ascii=False)
    print(f"Updated ch{ch} with {len(full)} items.")
