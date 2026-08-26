"""
Auto-Sync Watcher Daemon for The 48 Laws of Power.
Runs in the background, checks for new acoustic files every 20 seconds,
and automatically aligns and updates The_48_Laws_of_Power_Interactive_Reader.html.
"""

import time
import os
import sys

PIPELINE_DIR = "/Users/lindy/Vault/My Python Productivity Script 2/interactive_reader_pipeline"
sys.path.append(PIPELINE_DIR)

from sync_48laws_continuous import sync_once

print("Starting Auto-Sync Watcher Daemon for The 48 Laws of Power...")
while True:
    try:
        count, updated = sync_once()
        if updated:
            print(f"[Watcher] Successfully updated reader! Total live chapters: {count} / 49")
        if count >= 49:
            print("[Watcher] All 49 chapters complete! Daemon exiting successfully.")
            break
    except Exception as e:
        print(f"[Watcher Error]: {e}")
    time.sleep(20)
