"""42 CFR Part 2 governance — substance-use disorder record heightened protection.

42 CFR Part 2 ("Confidentiality of Substance Use Disorder Patient Records")
is a federal regulation that provides **heightened protection** for SUD
treatment records, *stricter than HIPAA*. It applies to any federally
assisted SUD treatment program. Key differences from HIPAA:

1. **Specific consent required for *any* disclosure, including TPO.** Unlike
   HIPAA (where treatment/payment/operations disclosures don't need consent),
   Part 2 requires a specific written consent for *most* disclosures, and the
   consent must name the recipient, the purpose, and the amount/date.

2. **Re-disclosure prohibition.** A recipient of Part 2 records may NOT
   re-disclose them unless the patient gives new specific authorization.
   The standard Part 2 notice: "This information has been disclosed to you
   from records protected by Federal confidentiality rules (42 CFR Part 2).
   The Federal rules prohibit you from making any further disclosure of this
   information unless further disclosure is expressly permitted by the
   written consent of the person to whom it pertains or as otherwise
   permitted by 42 CFR Part 2."

3. **No disclosure without consent in most cases.** Even to law enforcement,
   Part 2 records generally require consent or a qualifying court order
   (not just a subpoena).

This module is the gate:
- ``Part2Consent`` — a specific written consent (recipient, purpose, expiry).
- ``Part2DisclosureRequest`` — a request to disclose SUD records.
- ``assess_part2_disclosure`` — returns a report: blocked (no valid consent)
  or allowed (consent covers it), with the re-disclosure prohibition notice
  attached to every permitted disclosure.

Praxis never discloses Part 2 records autonomously — every disclosure is a
SEND-class action held for clinician approval, and this gate is the
evidence surface that the specific consent exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DisclosureRecipient = Literal[
    "treating_provider",      # another treating provider (Part 2 allows with consent)
    "payer",                  # insurance
    "law_enforcement",        # generally requires court order or consent
    "court_subpoena",         # subpoena alone is NOT enough under Part 2
    "patient_request",        # the patient themselves
    "research",               # research under Part 2 (qualified)
    "audit_evaluation",       # program audit/evaluation
    "other",
]


@dataclass(frozen=True)
class Part2Consent:
    """A specific written consent to disclose SUD records under 42 CFR Part 2.

    Must name the recipient, the purpose, the amount of information, and the
    expiration date. Revocable.
    """
    consent_id: str
    patient_id: str
    recipient: str           # who may receive the records
    purpose: str
    expires_at: float        # 0 = no expiry (rare; Part 2 prefers a date)
    authorized_at: float
    revoked: bool = False
    amount_description: str = "all records"   # what may be disclosed


@dataclass(frozen=True)
class Part2DisclosureRequest:
    request_id: str
    patient_id: str
    state: str
    record_category: str          # "substance_use" / "sud_treatment" / "medication_assisted_treatment"
    recipient: str                # DisclosureRecipient
    requested_at: float
    purpose: str = ""


@dataclass
class Part2Finding:
    severity: str
    code: str
    message: str


@dataclass
class Part2DisclosureReport:
    request: Part2DisclosureRequest
    blocked: bool = True
    allowed: bool = False
    requires_patient_consent: bool = False
    requires_court_order: bool = False
    findings: list[Part2Finding] = field(default_factory=list)
    redis_prohibition_notice: str = ""

    def summary(self) -> str:
        return (f"{len(self.findings)} finding(s); blocked={self.blocked}; "
                f"requires_consent={self.requires_patient_consent}; "
                f"requires_court_order={self.requires_court_order}")


# The standard Part 2 re-disclosure prohibition notice that MUST accompany
# any permitted Part 2 disclosure.
PART2_REDISCLOSURE_NOTICE = (
    "This information has been disclosed to you from records protected by "
    "Federal confidentiality rules (42 CFR Part 2). The Federal rules "
    "prohibit you from making any further disclosure of this information "
    "unless further disclosure is expressly permitted by the written consent "
    "of the person to whom it pertains or as otherwise permitted by "
    "42 CFR Part 2. A general authorization for the release of medical or "
    "other information is NOT sufficient for this purpose."
)


def _consent_covers(consent: Part2Consent, request: Part2DisclosureRequest, *, now: float) -> bool:
    if consent.revoked:
        return False
    if (not all((consent.consent_id.strip(), consent.patient_id.strip(),
                 consent.recipient.strip(), consent.purpose.strip(),
                 consent.amount_description.strip())) or
            consent.authorized_at <= 0 or consent.authorized_at > now):
        return False
    if consent.patient_id != request.patient_id:
        return False
    if consent.expires_at <= 0 or consent.expires_at < now:
        return False
    if consent.recipient != request.recipient:
        return False
    return consent.purpose.casefold().strip() == request.purpose.casefold().strip()


def assess_part2_disclosure(
    request: Part2DisclosureRequest,
    consent: Part2Consent | None = None,
    *,
    now: float = 0.0,
) -> Part2DisclosureReport:
    """Gate a Part 2 SUD-record disclosure.

    Decision table:
    - No consent → blocked, requires_patient_consent (critical).
    - Consent but doesn't cover recipient/expired/revoked → blocked.
    - Law enforcement / court subpoena without a qualifying Part 2 court
      order → blocked, requires_court_order (Part 2 needs more than a
      subpoena).
    - Consent covers it (treating provider, payer, patient request, etc.)
      → allowed, re-disclosure prohibition notice attached.
    """
    import time as _t
    now_ts = _t.time() if now == 0.0 else now
    report = Part2DisclosureReport(request=request)

    recipient = request.recipient

    protected_categories = {
        "substance_use", "sud_treatment", "medication_assisted_treatment",
    }
    if (not all((request.request_id.strip(), request.patient_id.strip(),
                 request.state.strip(), recipient.strip(), request.purpose.strip())) or
            request.requested_at <= 0 or
            request.record_category.casefold().strip() not in protected_categories):
        report.findings.append(Part2Finding(
            "critical", "invalid_disclosure_request",
            "Part 2 request identity, purpose, timestamp, and record category are required.",
        ))
        return report

    # Law enforcement and bare subpoenas need a Part 2 court order, not just consent
    if recipient in ("law_enforcement", "court_subpoena"):
        report.findings.append(Part2Finding(
            "critical", "part2_court_order_required",
            f"Part 2 disclosure to {recipient!r} requires a qualifying court "
            f"order under 42 CFR §2.65 — a subpoena alone is not sufficient, "
            f"and patient consent alone does not authorize it. SEND held for "
            f"clinician + legal review.",
        ))
        report.requires_court_order = True
        report.blocked = True
        return report

    if consent is None:
        report.findings.append(Part2Finding(
            "critical", "no_part2_consent",
            f"Part 2 disclosure to {recipient!r} requires a specific written "
            f"patient consent under 42 CFR §2.31 — no consent on file. "
            f"General HIPAA TPO consent does NOT authorize Part 2 disclosures.",
        ))
        report.requires_patient_consent = True
        report.blocked = True
        return report

    if not _consent_covers(consent, request, now=now_ts):
        report.findings.append(Part2Finding(
            "critical", "consent_does_not_cover",
            f"consent {consent.consent_id} does not cover this disclosure "
            f"(recipient mismatch / expired / revoked). SEND held.",
        ))
        report.requires_patient_consent = True
        report.blocked = True
        return report

    # Consent covers it
    report.blocked = False
    report.allowed = True
    report.requires_patient_consent = False
    report.redis_prohibition_notice = PART2_REDISCLOSURE_NOTICE
    report.findings.append(Part2Finding(
        "info", "part2_disclosure_permitted",
        f"Part 2 disclosure to {recipient!r} permitted under consent "
        f"{consent.consent_id} (purpose: {consent.purpose}). The "
        f"re-disclosure prohibition notice MUST accompany the disclosure.",
    ))
    return report


def render_part2_report(report: Part2DisclosureReport) -> str:
    r = report.request
    lines = [
        "42 CFR Part 2 Disclosure Gate Report",
        f"Request: {r.request_id} | Patient: {r.patient_id} | State: {r.state}",
        f"Record: {r.record_category} | Recipient: {r.recipient}",
        f"Decision: {'PERMITTED' if report.allowed else 'BLOCKED'}",
        "=" * 60,
    ]
    for f in report.findings:
        marker = {"critical": "X", "high": "!", "medium": "*", "info": "i"}.get(f.severity, "?")
        lines.append(f"  [{f.severity.upper()}] {marker} {f.code}: {f.message}")
    lines.append(f"Summary: {report.summary()}")
    if report.allowed:
        lines.append("--- Re-disclosure Prohibition Notice (MUST accompany) ---")
        lines.append(PART2_REDISCLOSURE_NOTICE)
    return "\n".join(lines)