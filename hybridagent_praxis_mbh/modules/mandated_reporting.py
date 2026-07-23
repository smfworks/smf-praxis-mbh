"""Mandated-reporter workflow — child abuse / dependent-adult / elder.

MH clinicians are mandated reporters in every state of the 13-state
registry. When a patient (or a third party) discloses abuse of a child,
a dependent adult, or an elder, the clinician must file a report with
the state's social-services registry (SCR / CPS / APS) within the
state's window — typically 24 hours for child abuse.

This module is the workflow ledger:
1. **File** the incident — register it, set the SCR deadline from the
   state's ``child_abuse_scr_window_hours``, and mark ``requires_clinician_sign_off``.
2. **Sign off** — the clinician confirms the report was filed with the
   SCR. Filing the actual report with the SCR is a SEND-class action
   held for clinician approval; Praxis never files autonomously.
3. **Document** — the workflow is fully documented (closed).

Praxis never makes the mandated report as the reporter of record — the
clinician is the reporter. Praxis drafts the report scaffold, sets the
deadline, and holds the SEND for clinician sign-off.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .mh_jurisdictions import get_mh_profile

ReportReason = Literal[
    "child_abuse",          # abuse of a minor
    "dependent_adult_abuse",
    "elder_abuse",
    "neglect",
    "other",
]

ReportStatus = Literal[
    "filed",          # registered with Praxis; SCR filing pending clinician sign-off
    "signed_off",     # clinician confirmed the SCR report was filed
    "documented",     # workflow fully documented (closed)
]


@dataclass
class MandatedReportIncident:
    incident_id: str
    patient_id: str
    state: str
    reason: ReportReason
    description: str
    detected_at: float
    status: ReportStatus = "filed"
    signed_off_at: float = 0.0
    signed_off_by: str = ""
    deadline_at: float = 0.0          # detected_at + scr_window_hours
    documented_at: float = 0.0
    scr_reference: str = ""           # the SCR/CPS confirmation number (clinician records)


@dataclass
class MandatedReportFinding:
    severity: str
    code: str
    message: str


@dataclass
class MandatedReportResult:
    incident: MandatedReportIncident
    requires_clinician_sign_off: bool = False
    findings: list[MandatedReportFinding] = field(default_factory=list)

    @property
    def status(self) -> str:
        return self.incident.status

    @property
    def deadline_at(self) -> float:
        return self.incident.deadline_at

    def summary(self) -> str:
        return (f"{len(self.findings)} finding(s); status={self.incident.status}; "
                f"deadline={self.incident.deadline_at}; sign_off_required={self.requires_clinician_sign_off}")


class MandatedReportError(Exception):
    """Raised when a mandated-report workflow transition is invalid."""


def file_mandated_report(
    ledger: "MandatedReportLedger",
    incident: MandatedReportIncident,
    *,
    now: float = 0.0,
) -> MandatedReportResult:
    """Register a mandated-report incident and set the SCR deadline.

    The actual filing with the state SCR is a SEND-class action held for
    clinician sign-off — Praxis never files autonomously. This function
    registers the incident, computes the deadline from the state's
    ``child_abuse_scr_window_hours``, and returns a result flagging that
    clinician sign-off is required.
    """
    import time as _t
    now_ts = _t.time() if now == 0.0 else now
    prof = get_mh_profile(incident.state)
    result = MandatedReportResult(incident=incident)

    valid_reasons = {
        "child_abuse", "dependent_adult_abuse", "elder_abuse", "neglect", "other",
    }
    if (not all((incident.incident_id.strip(), incident.patient_id.strip(),
                 incident.state.strip(), incident.description.strip())) or
            incident.reason not in valid_reasons or
            incident.detected_at <= 0 or incident.detected_at > now_ts):
        result.findings.append(MandatedReportFinding(
            "critical", "invalid_incident_evidence",
            "incident identity, reason, description, and detection time are required",
        ))
        result.requires_clinician_sign_off = True
        return result

    if prof is None:
        result.findings.append(MandatedReportFinding(
            "critical", "unknown_jurisdiction",
            f"patient state {incident.state!r} is not in the MBH registry — "
            f"Praxis cannot set the SCR window; clinician must file under the "
            f"applicable state's rules",
        ))
        result.requires_clinician_sign_off = True
        incident.deadline_at = 0.0
        ledger._register(incident)
        return result

    window_hours = prof.child_abuse_scr_window_hours
    if window_hours <= 0:
        window_hours = 24  # fail-closed default
    incident.deadline_at = incident.detected_at + (window_hours * 3600)
    incident.status = "filed"
    result.requires_clinician_sign_off = True

    result.findings.append(MandatedReportFinding(
        "critical", "mandated_report_filed",
        f"{incident.reason} disclosure registered — clinician must file with "
        f"the state SCR within {window_hours}h (deadline {incident.deadline_at}). "
        f"Citation: {prof.mandated_report_citation}. Praxis does NOT file as the "
        f"reporter of record — SEND held for clinician sign-off.",
    ))
    if incident.reason in {"dependent_adult_abuse", "elder_abuse"}:
        result.findings.append(MandatedReportFinding(
            "high", "adult_protective_services_verification_required",
            "Adult/elder protective-services routing and deadline require "
            "jurisdiction-specific clinician verification; the conservative "
            "deadline must be confirmed before filing.",
        ))
    ledger._register(incident)
    return result


class MandatedReportLedger:
    """Append-only ledger of mandated-report incidents."""

    def __init__(self) -> None:
        self._incidents: dict[str, MandatedReportIncident] = {}

    def _register(self, incident: MandatedReportIncident) -> None:
        existing = self._incidents.get(incident.incident_id)
        if existing is not None and existing != incident:
            raise MandatedReportError("incident is immutable and cannot be overwritten")
        self._incidents[incident.incident_id] = incident

    def sign_off(
        self, incident_id: str, *, signed_off_by: str,
        signed_off_at: float, scr_reference: str = "",
    ) -> MandatedReportIncident:
        """Record that the clinician filed the report with the SCR."""
        inc = self._incidents.get(incident_id)
        if inc is None:
            raise MandatedReportError(f"incident {incident_id} not found")
        if inc.status != "filed":
            raise MandatedReportError(
                f"cannot sign off incident in status '{inc.status}' — must be 'filed'")
        if (not signed_off_by.strip() or not scr_reference.strip() or
                signed_off_at <= 0 or signed_off_at < inc.detected_at):
            raise MandatedReportError(
                "sign-off actor, SCR reference, and valid timestamp are required")
        if signed_off_at > inc.deadline_at:
            raise MandatedReportError(
                f"sign-off at {signed_off_at} is PAST the SCR deadline "
                f"{inc.deadline_at} — the state's window was missed")
        inc.signed_off_at = signed_off_at
        inc.signed_off_by = signed_off_by
        inc.scr_reference = scr_reference
        inc.status = "signed_off"
        return inc

    def document(self, incident_id: str, documented_at: float) -> MandatedReportIncident:
        """Close the incident — the mandated-report workflow is fully documented."""
        inc = self._incidents.get(incident_id)
        if inc is None:
            raise MandatedReportError(f"incident {incident_id} not found")
        if inc.status != "signed_off":
            raise MandatedReportError(
                f"cannot document incident in status '{inc.status}' — must be 'signed_off'")
        inc.documented_at = documented_at
        inc.status = "documented"
        return inc

    def get(self, incident_id: str) -> MandatedReportIncident | None:
        return self._incidents.get(incident_id)

    def all_incidents(self) -> list[MandatedReportIncident]:
        return list(self._incidents.values())

    def open_incidents(self) -> list[MandatedReportIncident]:
        return [i for i in self._incidents.values() if i.status != "documented"]


def render_mandated_report_log(ledger: MandatedReportLedger) -> str:
    """Render the mandated-report ledger as an audit-ready log."""
    lines = ["Mandated Report Log", "=" * 60]
    for inc in ledger.all_incidents():
        lines.append(
            f"  [{inc.incident_id}] state={inc.state} reason={inc.reason} "
            f"status={inc.status} deadline={inc.deadline_at}")
    lines.append(f"Total: {len(ledger.all_incidents())} incident(s)")
    return "\n".join(lines)