"""Crisis-safety gate — duty to warn / protect + safety-planning governance.

The MH vertical's analogue of the medical vertical's never-write-to-chart
guardrail, but for the highest-stakes MH scenario: a patient who may pose
a serious risk of physical violence to an identifiable victim, or who is
in acute suicidal crisis. Two distinct clinical-legal duties intersect:

1. **Duty to warn / protect (Tarasoff-line).** When a patient makes a
   credible serious threat of physical violence against a reasonably
   identifiable victim, a clinician may be *required* to take reasonable
   steps to protect the victim — warn the victim, notify law enforcement,
   or take other protective action.    The standard varies by state: codified (CA), mandatory statutory duty,
   case-law duty, permissive disclosure, or no duty verified. This module
   reads the state's ``duty_to_warn_standard`` from :mod:`mh_jurisdictions`
   and returns a report — it does NOT execute the warning. Executing a
   warning (SEND-class) is held for clinician approval.

2. **Suicidal-crisis safety planning.** When a patient is in acute suicidal
   crisis, the clinician's obligations are safety planning, means-restriction
   counseling, and (if needed) voluntary or involuntary evaluation. Praxis
   does not assess risk autonomously — it drafts a safety-plan scaffold for
   clinician review and surfaces the state's civil-commitment standard.
   ``DESTRUCTIVE`` means-restriction recommendations route through approval.

Design (non-negotiable):
- Praxis **never** determines that a duty to warn applies as a final
  clinical judgment; it flags the conditions that *trigger* a duty analysis
  and routes to the clinician. The clinician — not Praxis — decides.
- Praxis **never** contacts a victim, law enforcement, or a hospital
  autonomously. Every external contact is a SEND-class action held for
  clinician approval.
- The gate is fail-closed: a credible threat with an identifiable victim
  in a codified-duty state always triggers a ``duty_triggered=True`` report
  requiring clinician action.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .mh_jurisdictions import get_mh_profile


@dataclass(frozen=True)
class CrisisAssessment:
    """A structured crisis-safety assessment input.

    Fields are the facts Praxis uses to determine whether the conditions
    that *trigger* a duty analysis are present. Praxis does not
    independently verify these — the clinician supplies them.
    """
    assessment_id: str
    patient_id: str
    state: str                       # two-letter jurisdiction
    threat_credible: bool            # is there a credible serious threat of physical violence?
    identifiable_victim: bool        # is there a reasonably identifiable victim?
    patient_history_violence: bool = False   # known history of violence
    suicidal_ideation: bool = False          # acute suicidal ideation
    suicidal_plan: bool = False              # plan + means + intent
    intent_to_act: bool = False              # stated intent to act on the threat
    disclosed_at: float = 0.0


@dataclass
class DutyToWarnFinding:
    severity: str          # critical | high | medium | info
    code: str
    message: str


@dataclass
class DutyToWarnReport:
    assessment: CrisisAssessment
    duty_triggered: bool = False          # conditions for a duty analysis are present
    requires_clinician_action: bool = False
    standard: str = ""                    # the state's duty_to_warn_standard
    citation: str = ""
    findings: list[DutyToWarnFinding] = field(default_factory=list)

    def summary(self) -> str:
        n = len(self.findings)
        return (f"{n} finding(s); duty_triggered={self.duty_triggered}; "
                f"standard={self.standard}; action_required={self.requires_clinician_action}")


@dataclass(frozen=True)
class SafetyPlanDraft:
    """A drafted safety-plan scaffold for clinician review.

    Praxis drafts this; the clinician reviews and signs (or amends) via
    the treatment-planning attestation ledger. Praxis never delivers a
    safety plan to a patient autonomously — SEND is held.
    """
    draft_id: str
    patient_id: str
    state: str
    triggers: tuple[str, ...]
    coping_strategies: tuple[str, ...]
    supports: tuple[str, ...]
    means_restriction_recommendations: tuple[str, ...]
    drafted_at: float = 0.0


def assess_duty_to_warn(assessment: CrisisAssessment, *, now: float = 0.0) -> DutyToWarnReport:
    """Assess whether the conditions that trigger a duty-to-warn/protect
    analysis are present under the state's standard.

    Decision table:
    - Unknown jurisdiction → critical finding, duty_triggered=False (fail
      closed: the clinician must handle without Praxis's structured gate).
    - Credible threat + identifiable victim + (codified-duty OR
      duty-to-protect state) → ``duty_triggered=True``,
      ``requires_clinician_action=True``, critical finding.
    - Credible threat + identifiable victim + permissive-disclosure or
      no-duty state → ``duty_triggered=False`` but a high finding: the
      clinician must exercise professional judgment (a permissive statute
      allows disclosure; ethics may still require protective action).
    - No credible threat OR no identifiable victim → ``duty_triggered=False``;
      info finding that the threshold is not met.
    - Suicidal crisis is surfaced separately (does not trigger duty-to-warn
      but triggers a safety-plan recommendation).
    """
    import time as _t
    _t.time() if now == 0.0 else now  # mark now as used; no mutation
    report = DutyToWarnReport(assessment=assessment)
    state = assessment.state.upper()
    prof = get_mh_profile(state)
    if prof is None:
        report.findings.append(DutyToWarnFinding(
            "critical", "unknown_jurisdiction",
            f"patient state {state!r} is not in the MBH registry — "
            f"Praxis cannot evaluate the duty-to-warn standard; clinician "
            f"must handle outside the structured gate",
        ))
        report.requires_clinician_action = True
        return report

    report.standard = prof.duty_to_warn_standard
    report.citation = prof.duty_to_warn_citation

    credible = assessment.threat_credible and assessment.identifiable_victim

    if not credible:
        report.findings.append(DutyToWarnFinding(
            "info", "threshold_not_met",
            f"no credible serious threat against an identifiable victim — "
            f"the {prof.duty_to_warn_standard} threshold for a duty analysis "
            f"is not met ({prof.duty_to_warn_citation})",
        ))
        # still surface suicidal crisis if present
        if assessment.suicidal_ideation:
            report.findings.append(DutyToWarnFinding(
                "high", "suicidal_crisis_present",
                f"acute suicidal ideation flagged — safety-plan scaffold "
                f"recommended; civil-commitment standard: "
                f"{prof.civil_commitment_standard} ({prof.civil_commitment_citation})",
            ))
            report.requires_clinician_action = True
        return report

    # Credible threat against identifiable victim
    if prof.duty_to_warn_standard in ("tarasoff_codified", "tarasoff_common_law", "duty_to_protect"):
        report.duty_triggered = True
        report.requires_clinician_action = True
        discharge = prof.duty_discharge or "warn victim / notify law enforcement / hospitalize"
        report.findings.append(DutyToWarnFinding(
            "critical", "duty_to_protect_triggered",
            f"credible threat against identifiable victim under "
            f"{prof.duty_to_warn_standard} — {prof.duty_to_warn_citation}. "
            f"Discharge described by the cited source: {discharge}. "
            f"Clinician must decide protective action. Praxis does NOT contact the "
            f"victim or law enforcement autonomously — SEND held. "
            f"Not legal or clinical advice.",
        ))
    elif prof.duty_to_warn_standard == "permissive_disclosure":
        report.findings.append(DutyToWarnFinding(
            "high", "permissive_disclosure",
            f"credible threat against identifiable victim. {state} permits "
            f"disclosure but this table did not verify a mandatory duty "
            f"({prof.duty_to_warn_citation}). Clinician must exercise "
            f"professional judgment — protective action may still be warranted. "
            f"Not legal or clinical advice.",
        ))
        report.requires_clinician_action = True
    else:
        # no statutory duty verified
        report.findings.append(DutyToWarnFinding(
            "high", "professional_judgment_required",
            f"credible threat against identifiable victim, but no mandatory "
            f"duty was verified for {state} ({prof.duty_to_warn_citation}). "
            f"Clinician must exercise professional judgment under ethics rules — "
            f"protective action may still be warranted. Not legal or clinical advice.",
        ))
        report.requires_clinician_action = True

    if assessment.patient_history_violence:
        report.findings.append(DutyToWarnFinding(
            "high", "violence_history",
            "patient has a known history of violence — elevates the need for "
            "clinician protective action",
        ))
    if assessment.intent_to_act:
        report.findings.append(DutyToWarnFinding(
            "critical", "stated_intent_to_act",
            "patient has stated intent to act on the threat — immediate "
            "clinician protective action required",
        ))

    return report


def draft_safety_plan(assessment: CrisisAssessment) -> SafetyPlanDraft:
    """Draft a safety-plan scaffold for clinician review.

    Praxis drafts the scaffold; the clinician reviews and signs (or amends)
    via the treatment-planning attestation ledger. Delivery to the patient
    (SEND) is held for clinician approval. Means-restriction recommendations
    that involve a ``DESTRUCTIVE`` action (e.g. firearm removal guidance that
    the patient must act on) route through approval.
    """
    prof = get_mh_profile(assessment.state)
    triggers = ("situational triggers the patient identified",)
    coping = ("grounding techniques", "reach out to a support person",
              "use the crisis line")
    supports: tuple[str, ...] = (
        "988 Suicide & Crisis Lifeline (call/text 988)",
        "patient's identified support person",
    )
    means = ("discuss means-restriction with the clinician",
             "secure or remove access to lethal means if safe to do so")
    if prof is not None:
        supports = (*supports,
                    f"state crisis line ({prof.state_name})",
                    f"civil-commitment standard: {prof.civil_commitment_standard}")
    return SafetyPlanDraft(
        draft_id=f"sp-{assessment.assessment_id}",
        patient_id=assessment.patient_id,
        state=assessment.state,
        triggers=triggers,
        coping_strategies=coping,
        supports=supports,
        means_restriction_recommendations=means,
        drafted_at=assessment.disclosed_at,
    )


def render_duty_to_warn_report(report: DutyToWarnReport) -> str:
    """Render the duty-to-warn assessment for the clinician's review."""
    a = report.assessment
    lines = [
        "Duty-to-Warn / Protect Assessment (clinician review)",
        f"Assessment: {a.assessment_id} | Patient: {a.patient_id} | State: {a.state}",
        f"Standard: {report.standard} | Citation: {report.citation}",
        (f"Duty triggered: {report.duty_triggered} | "
        f"Clinician action required: {report.requires_clinician_action}"),
        "=" * 60,
    ]
    if not report.findings:
        lines.append("No findings.")
    for f in report.findings:
        marker = {"critical": "X", "high": "!", "medium": "*", "info": "i"}.get(f.severity, "?")
        lines.append(f"  [{f.severity.upper()}] {marker} {f.code}: {f.message}")
    lines.append(f"Summary: {report.summary()}")
    lines.append("NOTE: Praxis does NOT contact the victim or law enforcement "
                 "autonomously. Every external contact is a SEND-class action "
                 "held for clinician approval.")
    lines.append("NOT LEGAL OR CLINICAL ADVICE. Verify with your state board and counsel.")
    return "\n".join(lines)