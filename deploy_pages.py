"""
Module: deploy_pages.py
Description: Synchronizes compiled master reader and new audio tracks to GitHub Pages repo (Vault/Audible).
"""

import os
import shutil
import subprocess
import sys

def deploy_to_audible(master_html_path, audio_files, commit_message="update: deploy latest interactive reader"):
    audible_dir = "/Users/lindy/Vault/Audible"
    audible_index = os.path.join(audible_dir, "index.html")
    audible_audio_dir = os.path.join(audible_dir, "audio")
    
    os.makedirs(audible_audio_dir, exist_ok=True)
    
    # 1. Copy master HTML to index.html
    shutil.copyfile(master_html_path, audible_index)
    print(f"Copied {master_html_path} -> {audible_index}")
    
    # 2. Copy audio files
    for src in audio_files:
        if os.path.exists(src):
            dst = os.path.join(audible_audio_dir, os.path.basename(src))
            shutil.copyfile(src, dst)
            print(f"Copied {src} -> {dst}")
            
    # 3. Git commit and push
    subprocess.run(["git", "add", "index.html", "audio"], cwd=audible_dir, check=True)
    
    res = subprocess.run(["git", "commit", "-m", commit_message], cwd=audible_dir, capture_output=True, text=True)
    if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
        print("Nothing to commit in Vault/Audible.")
    else:
        print(f"Committed in Vault/Audible: {commit_message}")
        
    print("Pushing to GitHub origin main...")
    subprocess.run(["git", "push", "origin", "main"], cwd=audible_dir, check=True)
    print("Successfully deployed to GitHub Pages! URL: https://zack1997999.github.io/Audible/")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        master_html = sys.argv[1]
        audio_list = sys.argv[2:] if len(sys.argv) >= 3 else []
        deploy_to_audible(master_html, audio_list)
    else:
        print("Usage: python3 deploy_pages.py <master_html_path> [audio_file_1 audio_file_2 ...]")
