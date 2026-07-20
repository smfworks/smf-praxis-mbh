"""Treatment-plan attestation — never write the treatment plan autonomously.

The MH vertical's analogue of the medical vertical's never-write-to-chart
guardrail, applied to the treatment plan. The treatment plan is the
clinician-authored clinical record that sets goals, objectives, modality,
and frequency of care. Praxis **never writes the treatment plan
autonomously** — it drafts the plan scaffold, the clinician reviews and
signs (or amends), and only then does the draft enter the clinical record.

Design (mirrors ``clinical_attestation``):
- ``TreatmentPlanDraft`` — a drafted treatment plan (initial, 90-day
  review, discharge) with the chart id, patient id, content hash, and
  provenance.
- ``TreatmentPlanAttestation`` — the clinician's recorded review-and-sign.
- ``TreatmentPlanLedger`` — append-only. A clinical-record write is blocked
  unless ``can_write_plan(draft_id)`` returns True.

The governance line is non-negotiable: the treatment plan is a clinical
record, and an AI writing it without clinician sign-off is the unauthorized
practice of the mental-health profession. This module is the evidence
surface that the sign-off happened.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PlanType = Literal[
    "initial_treatment_plan",
    "treatment_plan_review",      # periodic (e.g. 90-day) review
    "discharge_plan",
    "safety_plan",                # crisis safety plan (see crisis_safety_gate)
]

AttestationType = Literal["signed", "amended", "rejected"]


@dataclass(frozen=True)
class TreatmentPlanDraft:
    draft_id: str
    chart_id: str
    patient_id: str
    plan_type: str
    content_hash: str
    drafted_by: str = "praxis"
    drafted_at: float = 0.0


@dataclass(frozen=True)
class TreatmentPlanAttestation:
    attestation_id: str
    draft_id: str
    clinician_id: str
    attestation_type: AttestationType
    attested_at: float
    edits_summary: str = ""
    edit_hash: str = ""


class TreatmentPlanAttestationError(Exception):
    """Raised when a treatment-plan write is attempted without a valid attestation."""


class TreatmentPlanLedger:
    """Append-only ledger of treatment-plan attestations.

    The clinical-record-write gate: ``can_write_plan(draft_id)`` returns
    True only if a ``signed`` or ``amended`` attestation exists for that
    draft.
    """

    def __init__(self) -> None:
        self._drafts: dict[str, TreatmentPlanDraft] = {}
        self._attestations: list[TreatmentPlanAttestation] = []

    def register_draft(self, draft: TreatmentPlanDraft) -> None:
        self._drafts[draft.draft_id] = draft

    def get_draft(self, draft_id: str) -> TreatmentPlanDraft | None:
        return self._drafts.get(draft_id)

    def attest(self, attestation: TreatmentPlanAttestation) -> TreatmentPlanAttestation:
        if attestation.draft_id not in self._drafts:
            raise TreatmentPlanAttestationError(
                f"cannot attest draft {attestation.draft_id} — not registered")
        existing = [a for a in self._attestations
                    if a.draft_id == attestation.draft_id
                    and a.attestation_type in ("signed", "amended")]
        if existing and attestation.attestation_type in ("signed", "amended"):
            return existing[0]
        self._attestations.append(attestation)
        return attestation

    def can_write_plan(self, draft_id: str) -> bool:
        return any(
            a.draft_id == draft_id and a.attestation_type in ("signed", "amended")
            for a in self._attestations
        )

    def has_attestation(self, draft_id: str) -> bool:
        return any(a.draft_id == draft_id for a in self._attestations)

    def pending_drafts(self) -> list[TreatmentPlanDraft]:
        signed = {a.draft_id for a in self._attestations
                  if a.attestation_type in ("signed", "amended")}
        rejected = {a.draft_id for a in self._attestations
                    if a.attestation_type == "rejected"}
        return [d for d in self._drafts.values()
                if d.draft_id not in signed and d.draft_id not in rejected]


def require_treatment_plan_attestation(
    ledger: TreatmentPlanLedger, draft_id: str,
) -> None:
    """Raise if the treatment-plan draft has no signed/amended attestation.

    Call this before any clinical-record-write path to enforce the
    never-write-the-plan-autonomously rule.
    """
    if not ledger.can_write_plan(draft_id):
        raise TreatmentPlanAttestationError(
            f"clinical-record write blocked for treatment-plan draft {draft_id} — "
            f"no clinician attestation (signed or amended). The treatment plan is "
            f"a clinical record; Praxis never writes it autonomously.")


def render_treatment_plan_log(ledger: TreatmentPlanLedger) -> str:
    lines = ["Treatment-Plan Attestation Log", "=" * 60]
    for a in ledger._attestations:
        d = ledger.get_draft(a.draft_id)
        chart = d.chart_id if d else "?"
        patient = d.patient_id if d else "?"
        edits = f" | edits: {a.edits_summary}" if a.edits_summary else ""
        lines.append(
            f"  [{a.attested_at}] draft={a.draft_id} chart={chart} "
            f"patient={patient} clinician={a.clinician_id} type={a.attestation_type}{edits}")
    lines.append(f"Total: {len(ledger._attestations)} attestation(s)")
    return "\n".join(lines)