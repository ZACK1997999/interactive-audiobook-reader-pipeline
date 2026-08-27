"""In-process release authorization shared by the validator and HTML compiler."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import secrets


class ReleaseAuthorizationError(RuntimeError):
    """Raised when HTML compilation lacks an authentic passing release gate."""


@dataclass(frozen=True)
class ReleaseToken:
    book_dir: str
    report_path: str
    report_sha256: str
    nonce: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def issue_release_token(book_dir: Path, report_path: Path, report: dict) -> ReleaseToken:
    if report.get("release_ready") is not True or report.get("errors") or report.get("warnings"):
        raise ReleaseAuthorizationError("Cannot issue release token for a failed validation report")
    return ReleaseToken(
        book_dir=str(book_dir.resolve()),
        report_path=str(report_path.resolve()),
        report_sha256=_sha256(report_path),
        nonce=secrets.token_urlsafe(24),
    )


def verify_release_token(token: ReleaseToken, book_dir: Path, report_path: Path) -> None:
    if not isinstance(token, ReleaseToken):
        raise ReleaseAuthorizationError("HTML compilation requires a validator-issued ReleaseToken")
    book_dir = Path(book_dir).resolve()
    report_path = Path(report_path).resolve()
    if token.book_dir != str(book_dir) or token.report_path != str(report_path):
        raise ReleaseAuthorizationError("Release token does not belong to this book/report")
    if not report_path.is_file() or _sha256(report_path) != token.report_sha256:
        raise ReleaseAuthorizationError("Release validation report is missing or was modified")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReleaseAuthorizationError("Release validation report is not valid JSON") from exc
    if report.get("release_ready") is not True or report.get("errors") or report.get("warnings"):
        raise ReleaseAuthorizationError("Release validation report does not authorize compilation")
