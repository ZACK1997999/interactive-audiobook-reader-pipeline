# Portability and publishing boundary

This repository contains the reusable pipeline code and specifications only.

Do not commit commercially purchased EPUBs, audiobooks, full book text, private notes, API keys, or machine-specific credentials. Keep those files in a local/private content repository or another storage system you control.

The current snapshot was developed on macOS and still contains some legacy absolute paths. Portability refactoring is intentionally a later iteration. Before running on another computer, replace those paths with command-line arguments or a local configuration file that is ignored by Git.

The generated reader may contain copyrighted book text and audio. Treat generated readers as private unless you have permission to redistribute their contents.
