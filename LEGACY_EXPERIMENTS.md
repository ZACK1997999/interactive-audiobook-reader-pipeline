# Legacy and book-specific experiments

The reusable release path is limited to the documented entry points in
`README.md` and `REPRODUCE.md`. Older scripts for a particular book or one
processing run remain in the repository as historical reference, but are not
installed as package commands and must not be used to publish a reader without
the release gate.

Examples include the 48 Laws watcher/adapter and older Range batch helpers.
When the same behavior is needed for a second book, extract the behavior into
the generic pipeline and add a regression fixture; do not copy the script and
hardcode a new book path.
