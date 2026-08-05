"""Minor-consent record gate for mental/behavioral health encounters.

The MH-vertical analogue of the medical vertical's ``minor_consent`` module,
scoped to mental/behavioral health outpatient services. State laws vary on
(a) the minimum age at which a minor may self-consent to outpatient MH
treatment without a parent, and (b) whether a parent may access the records
of those encounters.

Across the 13-state MBH registry every state encodes:

- ``minor_mh_consent_age`` — the minimum age for self-consent to outpatient MH
- ``minor_mh_parent_access_restricted`` — parent access to self-consented
  MH encounter records is restricted (True in all 13)
- ``minor_mh_consent_citation`` — the statute

This module enforces the gate:

1. **Classify the encounter.** Is the service an outpatient MH encounter?
   Was the minor the self-consenting patient and at/above the state's
   ``minor_mh_consent_age``?
2. **Gate parent access.** When the encounter is a confidential minor-consent
   MH encounter, a parent/guardian request for that encounter's records is
   **denied** unless the minor has authorized the release.
3. **Minor authorization.** An explicit ``MinorMhReleaseAuthorization``
   unlocks parent access. Scoped to one encounter, time-bounded, revocable.

Praxis never discloses the confidential record content itself. This module
is a gate: allow / deny + findings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .mh_jurisdictions import get_mh_profile

MhServiceCategory = Literal[
    "outpatient_therapy",       # outpatient psychotherapy / counseling
    "intensive_outpatient",     # IOP
    "medication_management",    # psychiatric medication management
    "substance_use_treatment",  # SUD treatment (also 42 CFR Part 2 — see part2_governance)
    "crisis_assessment",        # crisis/safety assessment
    "general",                  # non-confidential routine
    "other",
]

RequesterRole = Literal[
    "minor_patient",
    "parent_guardian",
    "provider",
    "payer",
    "other",
]

AccessChannel = Literal[
    "portal_view",
    "record_release",
    "treatment_summary",
    "billing_statement",
    "other",
]


@dataclass(frozen=True)
class MinorMhEncounter:
    encounter_id: str
    patient_id: str
    state: str
    service_category: str
    self_consented: bool = False
    patient_age: int = 14
    encounter_at: float = 0.0


@dataclass(frozen=True)
class MinorMhReleaseAuthorization:
    authorization_id: str
    patient_id: str
    encounter_id: str
    authorized_recipient: str
    authorized_at: float
    expires_at: float = 0.0
    revoked: bool = False


@dataclass(frozen=True)
class MinorMhAccessRequest:
    request_id: str
    encounter_id: str
    requester_role: RequesterRole
    requester_id: str
    channel: AccessChannel = "portal_view"
    purpose: str = "patient_access"


@dataclass
class MinorMhAccessFinding:
    severity: str
    code: str
    message: str
    state: str


@dataclass
class MinorMhAccessReport:
    request: MinorMhAccessRequest
    encounter: MinorMhEncounter
    allowed: bool = False
    confidential: bool = False
    findings: list[MinorMhAccessFinding] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return not self.allowed

    def summary(self) -> str:
        return (f"{len(self.findings)} finding(s); confidential={self.confidential}; "
                f"allowed={self.allowed}")


class MinorMhConsentError(Exception):
    """Raised when a confidential minor MH record is accessed without authorization."""


_CONFIDENTIAL_MH_CATEGORIES = frozenset({
    "outpatient_therapy", "intensive_outpatient", "medication_management",
    "substance_use_treatment", "crisis_assessment",
})


def is_confidential_minor_mh_encounter(encounter: MinorMhEncounter) -> bool:
    """True if the encounter is a confidential minor-consent MH encounter
    in the patient's state AND the minor self-consented at/above the
    state's ``minor_mh_consent_age``."""
    prof = get_mh_profile(encounter.state)
    if prof is None:
        return False
    category = encounter.service_category.lower().strip()
    if category not in _CONFIDENTIAL_MH_CATEGORIES:
        return False
    if not encounter.self_consented:
        return False
    return encounter.patient_age >= prof.minor_mh_consent_age


def _authorization_covers(
    auth: MinorMhReleaseAuthorization,
    encounter: MinorMhEncounter,
    requester: MinorMhAccessRequest,
    *,
    now: float,
) -> bool:
    if auth.revoked:
        return False
    if (not auth.authorization_id.strip() or auth.authorized_at <= 0 or
            auth.authorized_at > now):
        return False
    if auth.patient_id != encounter.patient_id:
        return False
    if auth.encounter_id != encounter.encounter_id:
        return False
    if auth.expires_at and auth.expires_at < now:
        return False
    return not (auth.authorized_recipient not in (requester.requester_id, requester.requester_role, "parent_guardian") and not (requester.requester_role == "parent_guardian" and auth.authorized_recipient in ("parent_guardian", "parent", "guardian")))


def check_minor_mh_record_access(
    request: MinorMhAccessRequest,
    encounter: MinorMhEncounter,
    authorizations: list[MinorMhReleaseAuthorization] | None = None,
    *,
    now: float = 0.0,
) -> MinorMhAccessReport:
    """Gate access to a minor's MH encounter records.

    Decision table:
    - Unknown jurisdiction → deny (fail closed)
    - Adult patient (age >= 18) → allow (gate does not apply)
    - Non-confidential encounter → allow
    - Confidential + requester is the minor patient → allow
    - Confidential + requester is provider → allow (treatment)
    - Confidential + parent/guardian + authorization covers → allow
    - Confidential + parent/guardian + no authorization → **deny**
    - Confidential + other roles → deny (fail closed)
    """
    import time as _t
    now_ts = _t.time() if now == 0.0 else now
    report = MinorMhAccessReport(request=request, encounter=encounter)
    state = encounter.state.upper()

    if (request.encounter_id != encounter.encounter_id or
            not request.request_id.strip() or not request.requester_id.strip() or
            not encounter.encounter_id.strip() or not encounter.patient_id.strip()):
        report.findings.append(MinorMhAccessFinding(
            "critical", "identity_mismatch",
            "request and encounter identities are missing or do not match", state,
        ))
        return report

    prof = get_mh_profile(state)
    if prof is None:
        report.findings.append(MinorMhAccessFinding(
            "critical", "unknown_jurisdiction",
            f"patient state {state!r} is not in the MBH registry — "
            f"cannot evaluate minor-consent-for-MH rules",
            state,
        ))
        report.allowed = False
        return report

    if encounter.patient_age >= 18:
        report.allowed = True
        report.findings.append(MinorMhAccessFinding(
            "info", "adult_patient",
            f"patient age {encounter.patient_age} is adult — minor-consent gate does not apply",
            state,
        ))
        return report

    confidential = is_confidential_minor_mh_encounter(encounter)
    report.confidential = confidential

    if not confidential:
        report.allowed = True
        report.findings.append(MinorMhAccessFinding(
            "info", "not_confidential",
            f"encounter service {encounter.service_category!r} is not a "
            f"self-consented confidential MH service under {state} rules — "
            f"parent access unrestricted by this gate",
            state,
        ))
        return report

    report.findings.append(MinorMhAccessFinding(
        "info", "confidential_mh_service",
        f"encounter is a confidential minor-consent MH service "
        f"({encounter.service_category}) under {state} "
        f"(age floor {prof.minor_mh_consent_age}; {prof.minor_mh_consent_citation})",
        state,
    ))

    role = request.requester_role

    if role == "minor_patient":
        report.allowed = request.requester_id == encounter.patient_id
        report.findings.append(MinorMhAccessFinding(
            "info" if report.allowed else "critical",
            "minor_self_access" if report.allowed else "minor_identity_mismatch",
            "minor patient accessing their own confidential MH records — allowed"
            if report.allowed else "requester identity does not match the patient",
            state,
        ))
        return report

    if role == "provider":
        report.allowed = True
        report.findings.append(MinorMhAccessFinding(
            "info", "provider_access",
            "provider access to confidential minor-consent MH records (treatment) — allowed",
            state,
        ))
        return report

    if role == "parent_guardian":
        if not prof.minor_mh_parent_access_restricted:
            report.allowed = True
            report.findings.append(MinorMhAccessFinding(
                "info", "parent_access_not_restricted",
                f"{state} does not restrict parent access to minor-consent MH records — allowed",
                state,
            ))
            return report

        auths = authorizations or []
        covering = [a for a in auths
                    if _authorization_covers(a, encounter, request, now=now_ts)]
        if covering:
            report.allowed = True
            report.findings.append(MinorMhAccessFinding(
                "info", "minor_authorization_present",
                f"minor authorized release to {covering[0].authorized_recipient} "
                f"(auth {covering[0].authorization_id}) — parent access allowed",
                state,
            ))
            return report

        report.allowed = False
        report.findings.append(MinorMhAccessFinding(
            "critical", "parent_access_denied",
            f"parent/guardian access to confidential {encounter.service_category} "
            f"encounter denied under {state} minor-consent-for-MH rules — requires "
            f"the minor's explicit authorization ({prof.minor_mh_consent_citation})",
            state,
        ))
        return report

    report.allowed = False
    report.findings.append(MinorMhAccessFinding(
        "critical", "role_not_authorized",
        f"requester role {role!r} is not authorized to access confidential "
        f"minor-consent MH records without explicit release",
        state,
    ))
    return report