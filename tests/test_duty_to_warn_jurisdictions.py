"""Duty-to-warn classifications checked against the researched table.

NOT LEGAL OR CLINICAL ADVICE. These tests lock the corrected labels and
require every jurisdiction row to carry a citation or an explicit
unverified flag. They do not certify that a row is legal advice.
"""
from __future__ import annotations

import pytest

from hybridagent_praxis_mbh.modules.crisis_safety_gate import (
    CrisisAssessment,
    assess_duty_to_warn,
)
from hybridagent_praxis_mbh.modules.mh_jurisdictions import (
    all_duty_to_warn,
    get_duty_to_warn,
    get_mh_profile,
)

# Classifications corrected off the old "no statutory duty" label.
CORRECTED = {
    "NJ": "mandatory_duty",
    "OH": "mandatory_duty",
    "PA": "case_law_only",
    "MD": "mandatory_duty",
    "VA": "mandatory_duty",
    "FL": "mandatory_duty",
    "SC": "case_law_only",
    "TN": "mandatory_duty",
    "WV": "permissive_disclosure",
}

_STANDARD = {
    "mandatory_duty": "duty_to_protect",
    "case_law_only": "tarasoff_common_law",
    "permissive_disclosure": "permissive_disclosure",
    "no_duty_or_none_found": "no_statutory_duty",
}


def test_fifty_states_and_dc_are_present():
    rows = all_duty_to_warn()
    assert len(rows) == 51
    assert len({row.state for row in rows}) == 51
    assert "DC" in {row.state for row in rows}


@pytest.mark.parametrize("state,classification", list(CORRECTED.items()))
def test_corrected_duty_classifications(state, classification):
    entry = get_duty_to_warn(state)
    assert entry is not None
    assert entry.classification == classification
    assert entry.citation
    assert entry.source_url.startswith("http")
    assert entry.checked_on == "2026-09-30"
    profile = get_mh_profile(state)
    assert profile is not None
    assert profile.duty_classification == classification
    assert profile.duty_to_warn_standard == _STANDARD[classification]
    assert profile.duty_to_warn_citation == entry.citation


def test_every_entry_has_citation_or_unverified_flag():
    for entry in all_duty_to_warn():
        assert entry.citation or entry.verified is False
        assert entry.checked_on == "2026-09-30"
        assert entry.classification in _STANDARD
        if entry.verified is False:
            assert entry.note, entry.state


def test_profile_duty_fields_match_the_researched_table():
    """The 13-state profiles and the CA eval profile stay aligned with the table."""
    for state in ("FL", "GA", "SC", "TN", "VA", "WV", "MD", "PA", "OH", "NJ", "NY", "CT", "MA", "CA"):
        entry = get_duty_to_warn(state)
        profile = get_mh_profile(state)
        assert entry is not None and profile is not None
        expected = "tarasoff_codified" if state == "CA" else _STANDARD[entry.classification]
        assert profile.duty_to_warn_standard == expected
        assert profile.duty_classification == entry.classification
        assert profile.duty_verified is entry.verified


def test_mandatory_states_trigger_and_permissive_states_do_not():
    now = 1_780_000_000.0
    for state in ("NJ", "OH", "MD", "VA", "TN", "FL"):
        report = assess_duty_to_warn(
            CrisisAssessment("a", "p", state, threat_credible=True, identifiable_victim=True),
            now=now,
        )
        assert report.duty_triggered, state
        assert report.requires_clinician_action
    for state in ("WV", "CT"):
        report = assess_duty_to_warn(
            CrisisAssessment("a", "p", state, threat_credible=True, identifiable_victim=True),
            now=now,
        )
        assert not report.duty_triggered, state
        assert report.requires_clinician_action
        assert any(item.code == "permissive_disclosure" for item in report.findings)


def test_case_law_states_still_trigger_clinician_action():
    now = 1_780_000_000.0
    for state in ("PA", "SC"):
        report = assess_duty_to_warn(
            CrisisAssessment("a", "p", state, threat_credible=True, identifiable_victim=True),
            now=now,
        )
        assert report.duty_triggered, state
