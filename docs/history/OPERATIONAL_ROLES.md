# Operational roles

The reader workflow separates responsibility without introducing a second
pipeline:

| Role | May do | May not do |
|---|---|---|
| Producer | Create canonical text and linguistic analysis artifacts | Declare release readiness |
| Alignment Repairer | Generate aligned artifacts from verified acoustic evidence | Rewrite timestamps to hide missing evidence |
| Independent Verifier | Validate contracts, hashes, review decisions, and release invariants | Compile HTML or waive failures implicitly |
| Release Orchestrator | Request validation, receive the ReleaseToken, and compile the reader | Compile without a valid token or bypass the validator |

The verifier-issued `ReleaseToken` is bound to the validation report path and
SHA-256 digest. `html_builder.py` verifies that token before loading chapter
artifacts. A failed validation therefore cannot reach HTML compilation through
the official orchestration path.

Owner-approved audiobook variations belong in `reader_review_ledger.json`.
They preserve the original acoustic evidence and waive only the exact reviewed
sentence IDs.
