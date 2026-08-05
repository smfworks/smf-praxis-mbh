"""Behavioral Health pack — 13-state integration test.

Proves the pack works across all 13 registry states: MH profiles load,
duty-to-warn/protect behavior, mandated-reporter SCR windows, minor-consent-MH
gate, 42 CFR Part 2 SUD-record governance, psychotherapy-note gate,
treatment-plan attestation, records-retention + patient-access deadlines,
and pack persona/knowledge coverage.

Imports ``hybridagent_praxis_mbh`` once at module load so the vertical
registers with the base registry for the whole process lifetime (the
generic persona + posture cases are generated from the registered spec).
"""
from __future__ import annotations

import pytest

# Importing the package auto-registers the behavioral_health spec + eval
# factory with the base registry (process-global, idempotent).
import hybridagent_praxis_mbh  # noqa: F401
from hybridagent_praxis_mbh.modules.crisis_safety_gate import (
    CrisisAssessment,
    DutyToWarnReport,
    assess_duty_to_warn,
    draft_safety_plan,
)
from hybridagent_praxis_mbh.modules.mandated_reporting import (
    MandatedReportIncident,
    MandatedReportLedger,
    MandatedReportResult,
    file_mandated_report,
)
from hybridagent_praxis_mbh.modules.mh_jurisdictions import (
    get_mh_profile,
    mh_summary,
    registered_mh_states,
)
from hybridagent_praxis_mbh.modules.minor_consent_mh import (
    MinorMhAccessRequest,
    MinorMhEncounter,
    check_minor_mh_record_access,
    is_confidential_minor_mh_encounter,
)
from hybridagent_praxis_mbh.modules.part2_governance import (
    Part2Consent,
    Part2DisclosureRequest,
    assess_part2_disclosure,
)
from hybridagent_praxis_mbh.modules.psychotherapy_notes_governance import (
    PsychotherapyDraft,
    PsychotherapyNoteError,
    PsychotherapyNoteLedger,
    require_psychotherapy_note_attestation,
)
from hybridagent_praxis_mbh.modules.records_retention_mh import (
    MhPatientAccessRequest,
    MhRecordSet,
    assess_mh_retention,
    open_mh_access_request,
)
from hybridagent_praxis_mbh.modules.treatment_planning_attestation import (
    TreatmentPlanAttestationError,
    TreatmentPlanDraft,
    TreatmentPlanLedger,
    require_treatment_plan_attestation,
)

STATES = list(registered_mh_states())
NOW = 1_780_000_000.0  # fixed epoch for deterministic tests


# ---------------------------------------------------------------------------
# Registry + profiles
# ---------------------------------------------------------------------------

def test_13_states_registered():
    assert len(STATES) == 13
    expected = {"FL", "GA", "SC", "TN", "VA", "WV", "MD", "PA",
                "OH", "NJ", "NY", "CT", "MA"}
    assert set(STATES) == expected


@pytest.mark.parametrize("state", STATES)
def test_every_state_has_mh_profile(state):
    p = get_mh_profile(state)
    assert p is not None
    assert p.state == state.upper()
    assert p.board_name
    assert p.child_abuse_scr_window_hours > 0
    assert p.minor_mh_consent_age >= 13


def test_mh_summary_covers_all_states():
    rows = mh_summary()
    assert len(rows) == 13
    assert {r["state"] for r in rows} == set(STATES)


def test_ca_profile_exists_for_tarasoff_eval():
    """CA (outside the 13-state registry) carries the codified Tarasoff
    standard used by the duty-to-warn eval case."""
    ca = get_mh_profile("CA")
    assert ca is not None
    assert ca.duty_to_warn_standard == "tarasoff_codified"


# ---------------------------------------------------------------------------
# Duty to warn / protect
# ---------------------------------------------------------------------------

def test_ca_tarasoff_triggers_on_credible_identifiable_threat():
    report = assess_duty_to_warn(
        CrisisAssessment(
            "ca1", "p1", "CA",
            threat_credible=True, identifiable_victim=True,
            patient_history_violence=True,
        ),
        now=NOW,
    )
    assert isinstance(report, DutyToWarnReport)
    assert report.duty_triggered
    assert report.requires_clinician_action


def test_no_duty_when_threat_not_credible():
    report = assess_duty_to_warn(
        CrisisAssessment(
            "ca2", "p1", "CA",
            threat_credible=False, identifiable_victim=False,
        ),
        now=NOW,
    )
    assert not report.duty_triggered


@pytest.mark.parametrize("state", ["NY", "CT", "MA"])
def test_duty_to_protect_states_trigger(state):
    """NY/CT/MA impose a duty to protect; credible + identifiable + history
    triggers clinician action."""
    report = assess_duty_to_warn(
        CrisisAssessment(
            "ca3", "p1", state,
            threat_credible=True, identifiable_victim=True,
            patient_history_violence=True,
        ),
        now=NOW,
    )
    assert report.duty_triggered
    assert report.requires_clinician_action


def test_safety_plan_draft_scaffolds_means_restriction():
    plan = draft_safety_plan(
        CrisisAssessment(
            "ca4", "p1", "NY",
            threat_credible=False, identifiable_victim=False,
            suicidal_ideation=True, suicidal_plan=True,
        ),
    )
    assert plan.patient_id == "p1"
    assert plan.means_restriction_recommendations is not None


# ---------------------------------------------------------------------------
# Mandated reporting
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", STATES)
def test_child_abuse_filed_within_scr_window(state):
    ledger = MandatedReportLedger()
    result = file_mandated_report(
        ledger,
        MandatedReportIncident(
            "mr1", "p1", state, "child_abuse",
            "disclosed during therapy session", detected_at=NOW,
        ),
        now=NOW,
    )
    assert isinstance(result, MandatedReportResult)
    assert result.requires_clinician_sign_off  # Praxis never files as reporter
    profile = get_mh_profile(state)
    assert result.incident.deadline_at >= NOW  # deadline is in the future
    # SCR window (hours) → deadline_at - detected_at should be ~ the window
    window_s = (result.incident.deadline_at - NOW)
    assert window_s > 0
    assert window_s <= profile.child_abuse_scr_window_hours * 3600 + 1


def test_mandated_report_send_held_for_clinician_signoff():
    """Filing with the SCR is SEND-held; Praxis drafts, clinician files."""
    ledger = MandatedReportLedger()
    result = file_mandated_report(
        ledger,
        MandatedReportIncident(
            "mr2", "p1", "NY", "child_abuse",
            "disclosed", detected_at=NOW,
        ),
        now=NOW,
    )
    assert result.requires_clinician_sign_off


# ---------------------------------------------------------------------------
# Minor consent for MH
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", STATES)
def test_parent_denied_self_consented_outpatient(state):
    get_mh_profile(state)
    encounter = MinorMhEncounter(
        "enc-1", "p1", state, "outpatient_therapy",
        self_consented=True, patient_age=15,
    )
    assert is_confidential_minor_mh_encounter(encounter)
    report = check_minor_mh_record_access(
        MinorMhAccessRequest("r1", "enc-1", "parent_guardian", "parent-1"),
        encounter,
        None,
        now=NOW,
    )
    assert report.blocked
    assert report.confidential


def test_minor_self_access_allowed():
    """The minor patient's own access to their confidential MH record is
    allowed (the ``minor_patient`` requester role); parent/guardian is
    blocked without an explicit release authorization."""
    encounter = MinorMhEncounter(
        "enc-2", "p1", "NY", "outpatient_therapy",
        self_consented=True, patient_age=15,
    )
    report = check_minor_mh_record_access(
        MinorMhAccessRequest("r2", "enc-2", "minor_patient", "p1"),
        encounter,
        None,
        now=NOW,
    )
    assert report.allowed


def test_below_consent_age_parent_access_allowed():
    """A 10-year-old is below every state's MH consent floor; parent access
    is not blocked by the minor-consent gate."""
    encounter = MinorMhEncounter(
        "enc-3", "p1", "NY", "outpatient_therapy",
        self_consented=False, patient_age=10,
    )
    assert not is_confidential_minor_mh_encounter(encounter)


# ---------------------------------------------------------------------------
# 42 CFR Part 2 (SUD records)
# ---------------------------------------------------------------------------

def test_part2_disclosure_without_consent_blocked():
    report = assess_part2_disclosure(
        Part2DisclosureRequest(
            "dr1", "p1", "NY", "substance_use", "health_plan",
            requested_at=NOW, purpose="treatment_payment",
        ),
        consent=None,
        now=NOW,
    )
    assert report.blocked
    assert report.requires_patient_consent
    assert not report.requires_court_order


def test_part2_law_enforcement_requires_court_order():
    """Law enforcement / bare subpoena needs a qualifying Part 2 court order
    (§2.65), not just patient consent."""
    report = assess_part2_disclosure(
        Part2DisclosureRequest(
            "dr2", "p1", "NY", "substance_use", "law_enforcement",
            requested_at=NOW, purpose="investigation",
        ),
        consent=None,
        now=NOW,
    )
    assert report.blocked
    assert report.requires_court_order


def test_part2_with_valid_consent_permits_with_redisclosure_notice():
    consent = Part2Consent(
        "c1", "p1", "health_plan", "treatment_payment",
        expires_at=NOW + 86400, authorized_at=NOW, revoked=False,
        amount_description="full record",
    )
    report = assess_part2_disclosure(
        Part2DisclosureRequest(
            "dr3", "p1", "NY", "substance_use", "health_plan",
            requested_at=NOW, purpose="treatment_payment",
        ),
        consent=consent,
        now=NOW,
    )
    assert report.allowed
    assert report.redis_prohibition_notice  # notice MUST accompany


# ---------------------------------------------------------------------------
# Psychotherapy notes gate
# ---------------------------------------------------------------------------

def test_psychotherapy_note_draft_rejected():
    """Praxis may not draft a PSYCHOTHERAPY_NOTE — they are the clinician's
    private process notes (45 CFR §164.508)."""
    ledger = PsychotherapyNoteLedger()
    with pytest.raises(PsychotherapyNoteError):
        ledger.register_draft(
            PsychotherapyDraft(
                "pn1", "c1", "p1", "PSYCHOTHERAPY_NOTE",
                "hash", drafted_by="praxis", drafted_at=NOW,
            )
        )


def test_progress_note_write_blocked_without_attestation():
    ledger = PsychotherapyNoteLedger()
    ledger.register_draft(
        PsychotherapyDraft(
            "pn2", "c1", "p1", "PROGRESS_NOTE",
            "hash", drafted_by="praxis", drafted_at=NOW,
        )
    )
    with pytest.raises(PsychotherapyNoteError):
        require_psychotherapy_note_attestation(ledger, "pn2")
    assert not ledger.can_write_note("pn2")


# ---------------------------------------------------------------------------
# Treatment-plan attestation
# ---------------------------------------------------------------------------

def test_treatment_plan_write_blocked_without_attestation():
    ledger = TreatmentPlanLedger()
    ledger.register_draft(
        TreatmentPlanDraft(
            "tp1", "c1", "p1", "initial_treatment_plan",
            "hash", drafted_by="praxis", drafted_at=NOW,
        )
    )
    with pytest.raises(TreatmentPlanAttestationError):
        require_treatment_plan_attestation(ledger, "tp1")


# ---------------------------------------------------------------------------
# Records retention + patient access
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", STATES)
def test_recent_mh_record_active(state):
    a = assess_mh_retention(
        MhRecordSet(
            "rec-1", "p1", state, "clinical_record",
            last_visit_at=NOW - 86400 * 30, patient_age_at_last_visit=40,
        ),
        now=NOW,
    )
    assert a.status == "active"


@pytest.mark.parametrize("state", STATES)
def test_mh_patient_access_deadline_positive(state):
    wf = open_mh_access_request(
        MhPatientAccessRequest("a1", "p1", state, NOW, "clinical_record"),
    )
    assert wf.access_days >= 1
    assert wf.deadline_at > NOW


def test_psychotherapy_note_carve_out_flagged():
    """Psychotherapy notes carry the patient-access carve-out (45 CFR
    §164.528) regardless of state."""
    wf = open_mh_access_request(
        MhPatientAccessRequest("a2", "p1", "NY", NOW, "psychotherapy_note"),
    )
    assert wf.psychotherapy_note_carve_out


# ---------------------------------------------------------------------------
# Vertical registration + eval cases
# ---------------------------------------------------------------------------

def test_vertical_registered_in_base_registry():
    from hybridagent.verticals.registry import (
        get_vertical_spec,
        is_vertical_registered,
    )
    assert is_vertical_registered("behavioral_health")
    spec = get_vertical_spec("behavioral_health")
    assert spec is not None
    assert spec.compliance_mode == "enforced"


def test_vertical_eval_cases_all_pass():
    """All 8 vertical eval cases (2 generic + 6 manual) pass."""
    from hybridagent.vertical_evals import vertical_eval_cases
    cases = vertical_eval_cases()
    bh_cases = [c for c in cases if c.id.startswith("vertical.behavioral_health.")]
    assert len(bh_cases) == 8
    for c in bh_cases:
        ok, detail = c.run()
        assert ok, f"{c.id} failed: {detail}"


# ---------------------------------------------------------------------------
# Pack persona + knowledge coverage
# ---------------------------------------------------------------------------

def test_behavioral_health_persona_guardrails():
    from hybridagent import vertical_templates as vt
    from hybridagent.pack import VerticalPack
    t = vt.get_template("behavioral_health")
    assert t is not None
    pk = VerticalPack.from_manifest({**t, "name": "behavioral_health"})
    sp = pk.system_prompt.lower()
    assert "never write to the clinical record" in sp
    assert "do not diagnose" in sp
    assert "psychotherapy note" in sp
    assert "42 cfr part 2" in sp
    assert "duty-to-warn" in sp or "duty to warn" in sp
    assert "mandated" in sp
    assert "phi" in sp


def test_behavioral_health_knowledge_covers_13_states():
    from pathlib import Path

    import hybridagent_praxis_mbh as pkg
    kb = Path(pkg.__file__).parent / "packs" / "behavioral_health" / "knowledge.md"
    text = kb.read_text()
    for state in STATES:
        assert state in text, f"{state} missing from knowledge base"


def test_behavioral_health_skills_present():
    import json
    from pathlib import Path

    import hybridagent_praxis_mbh as pkg
    manifest = json.loads(
        (Path(pkg.__file__).parent / "packs" / "behavioral_health" / "pack.json").read_text()
    )
    names = {s["name"] for s in manifest["skills"]}
    for required in (
        "never-write-clinical-record",
        "duty-to-warn-gate",
        "mandated-reporter-workflow",
        "part2-sud-record-governance",
        "psychotherapy-note-specific-auth",
        "minor-consent-mh-gate",
        "treatment-plan-attestation",
        "records-retention-mh",
    ):
        assert required in names, f"missing skill {required}"


def test_behavioral_health_risk_policy_holds_send_and_destructive():
    import json
    from pathlib import Path

    import hybridagent_praxis_mbh as pkg
    manifest = json.loads(
        (Path(pkg.__file__).parent / "packs" / "behavioral_health" / "pack.json").read_text()
    )
    rp = manifest["riskPolicy"]
    dual = {x.lower() for x in rp.get("dualApprovalRisks", [])}
    assert "send" in dual
    assert "destructive" in dual
    auto = {x.lower() for x in rp.get("autonomousRisks", [])}
    assert "read" in auto
    assert "draft" in auto