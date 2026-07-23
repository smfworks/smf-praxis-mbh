"""Regression coverage for release-blocking MBH governance failures."""
from dataclasses import replace

import pytest

from hybridagent_praxis_mbh.modules.mandated_reporting import (
    MandatedReportIncident,
    MandatedReportLedger,
    file_mandated_report,
)
from hybridagent_praxis_mbh.modules.minor_consent_mh import (
    MinorMhAccessRequest,
    MinorMhEncounter,
    check_minor_mh_record_access,
)
from hybridagent_praxis_mbh.modules.part2_governance import (
    Part2Consent,
    Part2DisclosureRequest,
    assess_part2_disclosure,
)
from hybridagent_praxis_mbh.modules.psychotherapy_notes_governance import (
    PsychotherapyDraft,
    PsychotherapyNoteAttestation,
    PsychotherapyNoteError,
    PsychotherapyNoteLedger,
    SpecificAuthorization,
)
from hybridagent_praxis_mbh.modules.treatment_planning_attestation import (
    TreatmentPlanAttestation,
    TreatmentPlanAttestationError,
    TreatmentPlanDraft,
    TreatmentPlanLedger,
)

NOW = 2_000_000_000.0


def _request():
    return Part2DisclosureRequest(
        "r", "patient", "NY", "sud_treatment", "payer", NOW, "claims"
    )


def _consent():
    return Part2Consent(
        "c", "patient", "payer", "claims", NOW + 1000, NOW - 1000,
        amount_description="claim fields",
    )


@pytest.mark.parametrize(
    "change",
    [
        {"purpose": "other"},
        {"recipient": "*"},
        {"amount_description": ""},
    ],
)
def test_part2_consent_is_specific(change):
    consent = replace(_consent(), **change)
    assert assess_part2_disclosure(_request(), consent, now=NOW).blocked


def test_part2_valid_specific_consent_allows_with_notice():
    report = assess_part2_disclosure(_request(), _consent(), now=NOW)
    assert report.allowed and not report.blocked
    assert "42 CFR Part 2" in report.redis_prohibition_notice


def test_lowercase_psychotherapy_note_cannot_bypass_ai_drafting_guard():
    ledger = PsychotherapyNoteLedger()
    with pytest.raises(PsychotherapyNoteError):
        ledger.register_draft(
            PsychotherapyDraft("d", "chart", "patient", "psychotherapy_note", "h")
        )


def test_missing_note_and_mutated_note_fail_closed():
    ledger = PsychotherapyNoteLedger()
    assert not ledger.can_disclose("missing", "payer", now=NOW)
    draft = PsychotherapyDraft(
        "d", "chart", "patient", "PSYCHOTHERAPY_NOTE", "h1", drafted_by="clinician"
    )
    ledger.register_draft(draft)
    with pytest.raises(PsychotherapyNoteError, match="immutable"):
        ledger.register_draft(replace(draft, content_hash="h2"))


def test_psychotherapy_disclosure_requires_attestation_and_specific_authorization():
    ledger = PsychotherapyNoteLedger()
    ledger.register_draft(
        PsychotherapyDraft(
            "d", "chart", "patient", "PSYCHOTHERAPY_NOTE", "h", drafted_by="clinician"
        )
    )
    ledger.add_authorization(
        SpecificAuthorization("auth", "patient", "payer", "claims", NOW - 10, NOW + 10)
    )
    assert not ledger.can_disclose("d", "payer", now=NOW)
    ledger.attest(PsychotherapyNoteAttestation("a", "d", "clinician", "signed", NOW))
    assert ledger.can_disclose("d", "payer", now=NOW)


def test_treatment_plan_draft_is_immutable_and_attestation_terminal():
    ledger = TreatmentPlanLedger()
    draft = TreatmentPlanDraft("d", "chart", "patient", "initial_treatment_plan", "h1")
    ledger.register_draft(draft)
    with pytest.raises(TreatmentPlanAttestationError, match="immutable"):
        ledger.register_draft(replace(draft, content_hash="h2"))
    ledger.attest(TreatmentPlanAttestation("a", "d", "clinician", "signed", NOW))
    with pytest.raises(TreatmentPlanAttestationError, match="terminal"):
        ledger.attest(TreatmentPlanAttestation("r", "d", "clinician", "rejected", NOW + 1))


def test_minor_self_access_requires_matching_patient_identity():
    encounter = MinorMhEncounter("e", "minor-1", "NY", "outpatient_therapy", True, 16)
    request = MinorMhAccessRequest("r", "e", "minor_patient", "minor-2")
    assert check_minor_mh_record_access(request, encounter, now=NOW).blocked


def test_elder_report_surfaces_aps_verification_requirement():
    ledger = MandatedReportLedger()
    incident = MandatedReportIncident(
        "i", "patient", "NY", "elder_abuse", "reported abuse", NOW - 1
    )
    result = file_mandated_report(ledger, incident, now=NOW)
    assert any(
        item.code == "adult_protective_services_verification_required"
        for item in result.findings
    )
