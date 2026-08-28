"""Deploy Influence audiobook to the Audible bookshelf portal."""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
from PIL import Image

AUDIBLE_REPO = Path("/Users/lindy/Vault/Audible").resolve()
BOOK_SOURCE_DIR = Path("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Influence - Robert B. Cialdini").resolve()
RAW_COVER_PATH = Path("/Users/lindy/Vault/audiobook/Influence, New and Expanded The Psychology of Persuasion/Influence, New and Expanded .jpg").resolve()

BOOK_ID = "influence"
TARGET_BOOK_DIR = AUDIBLE_REPO / "books" / BOOK_ID
TARGET_COVER_PATH = AUDIBLE_REPO / "assets" / "covers" / f"{BOOK_ID}.jpg"
MANIFEST_PATH = AUDIBLE_REPO / "manifest.json"

def prepare_cover():
    print(f"Preparing cover image from {RAW_COVER_PATH} -> {TARGET_COVER_PATH}...")
    TARGET_COVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(RAW_COVER_PATH) as img:
        img = img.convert("RGB")
        w, h = img.size
        target_ratio = 2 / 3
        # Center-crop to 2:3
        if w / h > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        elif w / h < target_ratio:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        img = img.resize((800, 1200), Image.Resampling.LANCZOS)
        img.save(TARGET_COVER_PATH, "JPEG", quality=92, optimize=True)
    print(f"Cover image saved ({TARGET_COVER_PATH.stat().st_size} bytes)")

def stage_book():
    print(f"Staging book directory {TARGET_BOOK_DIR}...")
    TARGET_BOOK_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy Master HTML -> index.html
    master_html = BOOK_SOURCE_DIR / "Influence_Interactive_Reader_Master.html"
    dest_html = TARGET_BOOK_DIR / "index.html"
    shutil.copy2(master_html, dest_html)
    print(f"Copied {master_html.name} -> {dest_html} ({dest_html.stat().st_size} bytes)")
    
    # 2. Symlink audio
    audio_link = TARGET_BOOK_DIR / "audio"
    target_audio = BOOK_SOURCE_DIR / "audio"
    if audio_link.is_symlink() or audio_link.exists():
        if audio_link.is_symlink():
            audio_link.unlink()
        else:
            shutil.rmtree(audio_link)
    audio_link.symlink_to(target_audio, target_is_directory=True)
    print(f"Created symlink: {audio_link} -> {target_audio}")

def update_manifest():
    print(f"Updating bookshelf manifest {MANIFEST_PATH}...")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    
    entry = {
        "id": BOOK_ID,
        "title": "Influence, New and Expanded",
        "subtitle": "The Psychology of Persuasion",
        "author": "Robert B. Cialdini",
        "cover": f"assets/covers/{BOOK_ID}.jpg",
        "readerUrl": f"books/{BOOK_ID}/index.html?v=3.0.0",
        "chaptersCount": 11,
        "totalDuration": "20h 40m",
        "accentColor": "#b45309",
        "genre": "Psychology & Behavioral Science",
        "tags": [
            "Psychology",
            "Persuasion",
            "Influence",
            "Decision Making",
            "Behavior",
            "Mindset"
        ],
        "description": "The foundational and widely acclaimed masterwork on persuasion and compliance, breaking down the universal psychological principles that drive human behavior and decision-making.",
        "status": "Studio Audiobook"
    }
    
    books = manifest.get("books", [])
    updated = False
    for i, b in enumerate(books):
        if b.get("id") == BOOK_ID:
            books[i] = entry
            updated = True
            break
    if not updated:
        books.append(entry)
        
    manifest["books"] = books
    manifest["updatedAt"] = time.strftime("%Y-%m-%d")
    
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest successfully updated with {len(books)} books total.")

def git_commit_and_push():
    print("Committing and pushing to Git repository...")
    subprocess.run(["git", "add", "manifest.json", f"assets/covers/{BOOK_ID}.jpg", f"books/{BOOK_ID}/index.html"], cwd=str(AUDIBLE_REPO), check=True)
    
    # Check if there are changes to commit
    diff_status = subprocess.run(["git", "status", "--porcelain"], cwd=str(AUDIBLE_REPO), capture_output=True, text=True)
    if diff_status.stdout.strip():
        commit_msg = f"feat(bookshelf): deploy 'Influence, New and Expanded' (11 chapters, 20h 40m)"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(AUDIBLE_REPO), check=True)
        print("Git commit created successfully.")
        
        print("Pushing to remote origin main...")
        try:
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(AUDIBLE_REPO), capture_output=True, text=True, timeout=60)
            if push_res.returncode == 0:
                print("Git push successful!")
            else:
                print(f"Git push warning (can be synced later): {push_res.stderr}")
        except Exception as e:
            print(f"Git push skipped/failed: {e}")
    else:
        print("No changes to commit.")

def main():
    print("=" * 60)
    print("   DEPLOYING 'INFLUENCE' TO AUDIBLE BOOKSHELF")
    print("=" * 60)
    prepare_cover()
    stage_book()
    update_manifest()
    git_commit_and_push()
    print("\nSUCCESS! Influence is deployed and published to the bookshelf.")

if __name__ == "__main__":
    main()
