"""Psychotherapy-notes governance — the most protected PHI category.

HIPAA draws a hard line between "medical/mental-health records" (the
progress notes, diagnosis, treatment plan, meds — ordinary PHI) and
"psychotherapy notes" (the clinician's private, process-oriented notes
documenting the content of a counseling session, kept separate from the
rest of the record). 45 CFR §164.508 requires **specific authorization**
for *any* use or disclosure of psychotherapy notes — the general TPO
(treatment/payment/operations) consent that covers ordinary PHI does NOT
cover psychotherapy notes.

This means:
- A payer cannot demand psychotherapy notes without specific authorization.
- A parent cannot access a minor's psychotherapy notes via the general
  minor-consent gate (psychotherapy notes need their own authorization).
- Praxis **never writes psychotherapy notes autonomously** — they are the
  clinician's private process notes, authored by the clinician, and an AI
  drafting them would contaminate the clinician's private therapeutic
  reasoning. Praxis may draft *progress notes* (the ordinary PHI record),
  not psychotherapy notes.

Design (mirrors ``clinical_attestation`` + adds the specific-authorization
gate):
- ``NoteType`` distinguishes ``PSYCHOTHERAPY_NOTE`` (specific-auth required)
  from ``PROGRESS_NOTE`` (ordinary PHI, general consent covers TPO).
- ``PsychotherapyDraft`` — a drafted note. Praxis may only draft
  ``PROGRESS_NOTE``; a ``PSYCHOTHERAPY_NOTE`` draft is refused at
  registration.
- ``PsychotherapyNoteLedger`` — append-only. A write is blocked unless
  ``can_write_note(draft_id)`` returns True (clinician attestation) AND,
  for psychotherapy notes, a specific authorization is on file.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

NoteType = Literal[
    "PSYCHOTHERAPY_NOTE",   # process notes — specific authorization required (Praxis never drafts)
    "PROGRESS_NOTE",        # ordinary PHI progress note — Praxis may draft for clinician review
]

AttestationType = Literal["signed", "amended", "rejected"]


@dataclass(frozen=True)
class PsychotherapyDraft:
    draft_id: str
    chart_id: str
    patient_id: str
    note_type: str
    content_hash: str
    drafted_by: str = "praxis"
    drafted_at: float = 0.0


@dataclass(frozen=True)
class PsychotherapyNoteAttestation:
    attestation_id: str
    draft_id: str
    clinician_id: str
    attestation_type: AttestationType
    attested_at: float
    edits_summary: str = ""
    edit_hash: str = ""


@dataclass(frozen=True)
class SpecificAuthorization:
    """A patient's specific authorization to use/disclose psychotherapy notes.

    Required by 45 CFR §164.508 for any use or disclosure of psychotherapy
    notes beyond the clinician's own treatment use. Scoped, time-bounded,
    revocable, and must identify the recipient and purpose.
    """
    authorization_id: str
    patient_id: str
    recipient: str           # who the notes may be disclosed to
    purpose: str
    authorized_at: float
    expires_at: float = 0.0
    revoked: bool = False


class PsychotherapyNoteError(Exception):
    """Raised when a psychotherapy-note write lacks attestation or specific
    authorization, or when Praxis attempts to draft a PSYCHOTHERAPY_NOTE."""


class PsychotherapyNoteLedger:
    """Append-only ledger of psychotherapy-note attestations.

    The write gate: ``can_write_note(draft_id)`` returns True only if a
    ``signed`` or ``amended`` attestation exists. For PSYCHOTHERAPY_NOTE,
    ``can_disclose(draft_id, recipient)`` additionally requires a
    SpecificAuthorization on file.
    """

    def __init__(self) -> None:
        self._drafts: dict[str, PsychotherapyDraft] = {}
        self._attestations: list[PsychotherapyNoteAttestation] = []
        self._authorizations: list[SpecificAuthorization] = []

    def register_draft(self, draft: PsychotherapyDraft) -> None:
        # Praxis never drafts PSYCHOTHERAPY_NOTEs — they are the clinician's
        # private process notes. Only a clinician (drafted_by != "praxis")
        # may register a psychotherapy-note draft.
        if (draft.note_type == "PSYCHOTHERAPY_NOTE"
                and draft.drafted_by == "praxis"):
            raise PsychotherapyNoteError(
                f"Praxis may not draft a PSYCHOTHERAPY_NOTE (draft {draft.draft_id}) "
                f"— psychotherapy notes are the clinician's private process notes "
                f"and may not be AI-authored (45 CFR §164.508). Praxis may draft "
                f"PROGRESS_NOTEs only.")
        self._drafts[draft.draft_id] = draft

    def add_authorization(self, auth: SpecificAuthorization) -> None:
        self._authorizations.append(auth)

    def get_draft(self, draft_id: str) -> PsychotherapyDraft | None:
        return self._drafts.get(draft_id)

    def attest(self, attestation: PsychotherapyNoteAttestation) -> PsychotherapyNoteAttestation:
        if attestation.draft_id not in self._drafts:
            raise PsychotherapyNoteError(
                f"cannot attest draft {attestation.draft_id} — not registered")
        existing = [a for a in self._attestations
                    if a.draft_id == attestation.draft_id
                    and a.attestation_type in ("signed", "amended")]
        if existing and attestation.attestation_type in ("signed", "amended"):
            return existing[0]
        self._attestations.append(attestation)
        return attestation

    def can_write_note(self, draft_id: str) -> bool:
        return any(
            a.draft_id == draft_id and a.attestation_type in ("signed", "amended")
            for a in self._attestations
        )

    def can_disclose(self, draft_id: str, recipient: str, *, now: float = 0.0) -> bool:
        """For PSYCHOTHERAPY_NOTE, disclosure requires a SpecificAuthorization
        covering the recipient. PROGRESS_NOTE disclosure follows ordinary PHI
        rules (handled elsewhere)."""
        import time as _t
        now_ts = _t.time() if now == 0.0 else now
        d = self._drafts.get(draft_id)
        if d is None or d.note_type != "PSYCHOTHERAPY_NOTE":
            return True  # not a psychotherapy note; ordinary PHI rules apply
        for auth in self._authorizations:
            if auth.revoked:
                continue
            if auth.patient_id != d.patient_id:
                continue
            if auth.expires_at and auth.expires_at < now_ts:
                continue
            if auth.recipient in (recipient, "*"):
                return True
        return False

    def pending_drafts(self) -> list[PsychotherapyDraft]:
        signed = {a.draft_id for a in self._attestations
                  if a.attestation_type in ("signed", "amended")}
        rejected = {a.draft_id for a in self._attestations
                    if a.attestation_type == "rejected"}
        return [d for d in self._drafts.values()
                if d.draft_id not in signed and d.draft_id not in rejected]


def require_psychotherapy_note_attestation(
    ledger: PsychotherapyNoteLedger, draft_id: str,
) -> None:
    """Raise if the note draft has no signed/amended clinician attestation."""
    if not ledger.can_write_note(draft_id):
        raise PsychotherapyNoteError(
            f"clinical-record write blocked for note draft {draft_id} — no "
            f"clinician attestation (signed or amended). Praxis never writes "
            f"to the clinical record autonomously.")


def require_psychotherapy_note_authorization(
    ledger: PsychotherapyNoteLedger, draft_id: str, recipient: str, *,
    now: float = 0.0,
) -> None:
    """Raise if a PSYCHOTHERAPY_NOTE disclosure lacks specific authorization
    (45 CFR §164.508)."""
    if not ledger.can_disclose(draft_id, recipient, now=now):
        raise PsychotherapyNoteError(
            f"psychotherapy-note disclosure blocked for draft {draft_id} to "
            f"{recipient!r} — no specific authorization on file. "
            f"45 CFR §164.508 requires specific authorization for any use or "
            f"disclosure of psychotherapy notes; general TPO consent does not "
            f"cover them.")


def render_psychotherapy_note_log(ledger: PsychotherapyNoteLedger) -> str:
    lines = ["Psychotherapy-Note Attestation Log", "=" * 60]
    for a in ledger._attestations:
        d = ledger.get_draft(a.draft_id)
        ntype = d.note_type if d else "?"
        edits = f" | edits: {a.edits_summary}" if a.edits_summary else ""
        lines.append(
            f"  [{a.attested_at}] draft={a.draft_id} type={ntype} "
            f"clinician={a.clinician_id} attest={a.attestation_type}{edits}")
    lines.append(f"Total: {len(ledger._attestations)} attestation(s)")
    return "\n".join(lines)