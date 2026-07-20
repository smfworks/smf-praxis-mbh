"""Mental/behavioral health records retention + patient access.

The MH vertical's records-retention module. MH records follow the medical
retention floor (the state's adult/minor retention years), with two
MH-specific notes:

1. **Psychotherapy notes** are retained per the clinician's practice policy
   but are NOT subject to the ordinary patient-access right in the same way
   (45 CFR §164.528 carves out psychotherapy notes — the patient does not
   have an automatic right to inspect them; they need specific
   authorization to disclose). This module flags that carve-out.

2. **42 CFR Part 2 records** carry the re-disclosure prohibition
   indefinitely — the retention period doesn't extinguish the Part 2
   protections.

Patient access deadlines follow the medical floor: NY/MA = 10 days,
FL/VA = 15, NJ = 7, MD = 21, others the HIPAA 30-day floor when the state
encodes 0.

This module loads the MH profile's retention fields instead of hardcoding.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .mh_jurisdictions import get_mh_profile

HIPAA_ACCESS_DAYS_FLOOR = 30  # 45 CFR §164.524(b) floor when a state encodes 0

RecordStatus = Literal["active", "eligible_for_disposal", "legal_hold", "disposed"]


@dataclass(frozen=True)
class MhRecordSet:
    record_id: str
    patient_id: str
    state: str
    record_type: str = "general_mh"   # general_mh | psychotherapy_note | sud_part2
    last_visit_at: float = 0.0
    patient_age_at_last_visit: int = 18


@dataclass(frozen=True)
class MhPatientAccessRequest:
    request_id: str
    patient_id: str
    state: str
    requested_at: float
    record_type: str = "general_mh"


@dataclass
class MhRetentionAssessment:
    record: MhRecordSet
    status: RecordStatus = "active"
    eligible_disposal_at: float = 0.0
    findings: list[str] = field(default_factory=list)
    psychotherapy_note_carve_out: bool = False
    part2_redis_prohibition_persists: bool = False

    def __post_init__(self):
        pass


@dataclass
class MhAccessWorkflow:
    request: MhPatientAccessRequest
    access_days: int = 0
    deadline_at: float = 0.0
    psychotherapy_note_carve_out: bool = False


def assess_mh_retention(record: MhRecordSet, *, now: float = 0.0) -> MhRetentionAssessment:
    """Assess retention status for an MH record set."""
    import time as _t
    now_ts = _t.time() if now == 0.0 else now
    prof = get_mh_profile(record.state)
    assessment = MhRetentionAssessment(record=record)

    if prof is None:
        assessment.status = "legal_hold"
        assessment.findings.append(
            f"unknown jurisdiction {record.state!r} — fail closed to legal hold")
        return assessment

    adult_years = prof.record_retention_adult_years
    minor_years = prof.record_retention_minor_years
    is_minor_record = record.patient_age_at_last_visit < 18
    years = minor_years if is_minor_record else adult_years
    assessment.eligible_disposal_at = record.last_visit_at + (years * 365.25 * 86400)

    if record.record_type == "psychotherapy_note":
        assessment.psychotherapy_note_carve_out = True
        assessment.findings.append(
            "psychotherapy note — patient-access carve-out applies (45 CFR "
            "§164.528; specific authorization required to disclose). Retained "
            "per clinician practice policy.")
    if record.record_type == "sud_part2":
        assessment.part2_redis_prohibition_persists = True
        assessment.findings.append(
            "42 CFR Part 2 SUD record — re-disclosure prohibition persists; "
            "retention period does not extinguish Part 2 protections.")

    if now_ts >= assessment.eligible_disposal_at:
        assessment.status = "eligible_for_disposal"
        assessment.findings.append(
            f"record eligible for disposal after {years}yr retention "
            f"({prof.record_retention_citation})")
    else:
        assessment.status = "active"
        assessment.findings.append(
            f"record active — {years}yr retention not yet satisfied "
            f"({prof.record_retention_citation})")

    return assessment


def open_mh_access_request(req: MhPatientAccessRequest) -> MhAccessWorkflow:
    """Open a patient access request; compute the deadline from the state's
    patient-access window (reuses the medical floor: NY/MA=10d, etc.)."""
    get_mh_profile(req.state)
    wf = MhAccessWorkflow(request=req)

    # MH patient-access deadlines track the medical floor; the MhProfile
    # doesn't re-encode them so we apply the known per-state values and
    # fall back to the HIPAA 30-day floor.
    per_state_days = {"NY": 10, "MA": 10, "FL": 15, "VA": 15, "NJ": 7, "MD": 21}
    days = per_state_days.get(req.state.upper(), 0)
    if days <= 0:
        days = HIPAA_ACCESS_DAYS_FLOOR
    wf.access_days = days
    wf.deadline_at = req.requested_at + (days * 86400)

    if req.record_type == "psychotherapy_note":
        wf.psychotherapy_note_carve_out = True
        wf.access_days = 0
        wf.deadline_at = 0.0

    return wf