"""Mental/Behavioral Health jurisdiction profiles.

Per-state regulatory facts the MBH vertical needs that the base's
``MedicalProfile`` does not carry. The base ``MedicalProfile`` encodes
minor-consent categories (including ``behavioral_health`` and
``substance_use``) and general medical-record retention, but the MBH
vertical additionally needs:

- **Duty-to-warn / Tarasoff** — whether the state imposes a duty to
  protect/warn an identifiable victim of a credible serious threat, and
  the citation (Tarasoff v. Regents, state codifications).
- **Mandated reporting** — the reporter categories, the SCR hotline window
  for child abuse, and the citation.
- **Civil commitment** — the standard and citation for involuntary
  evaluation/treatment.
- **42 CFR Part 2** — federal SUD-record heightened protection applies in
  every state, but the state's *consistency* statute (whether state law
  permits Part 2 re-disclosure under the same conditions) varies.
- **Psychotherapy notes** — HIPAA 45 CFR §164.508 requires specific
  authorization for psychotherapy notes in every state; this records
  whether the state adds any extra protection.
- **Minor consent for MH** — the minimum age and the citation for a
  minor to self-consent to outpatient mental health treatment (overlaps
  the base ``minor_consent_services`` but pinpoints the MH age floor).

Profiles are frozen dataclasses, one per state, loaded lazily. The
13-state registry matches the medical vertical's coverage: FL, GA, SC,
TN, VA, WV, MD, PA, OH, NJ, NY, CT, MA.

The duty-to-warn / duty-to-protect facts for all 50 states and the
District of Columbia live in :mod:`duty_to_warn_registry` and are applied
to each profile below. NOT LEGAL OR CLINICAL ADVICE. Verify with your
state board and counsel. Clinicians remain the decision-makers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .duty_to_warn_registry import (
    NOT_LEGAL_ADVICE,
    DutyToWarnEntry,
    all_duty_to_warn,
    get_duty_to_warn,
)

DutyToWarnStandard = Literal[
    "tarasoff_codified",      # statutory duty kept under the CA eval label
    "tarasoff_common_law",    # duty recognized by case law only
    "duty_to_protect",        # mandatory statutory duty to warn or protect
    "permissive_disclosure",  # statute allows disclosure; no duty verified
    "no_statutory_duty",      # no duty statute or binding duty opinion verified
]

MandatedReporterScope = Literal[
    "all_clinicians",         # all licensed MH professionals are reporters
    "mh_professionals",       # MH-specific reporter statute
    "all_adults",             # all adults are reporters (e.g. TX)
]


@dataclass(frozen=True)
class MhProfile:
    """Per-state mental/behavioral health regulatory facts.

    The MBH vertical's compliance modules load these instead of hardcoding.
    Fields are decision-support ground; the clinician remains the
    decision-maker and Praxis never diagnoses or determines treatment.
    """

    state: str                          # two-letter code, e.g. "MA"
    state_name: str
    board_name: str                     # state MH licensing board / agency
    board_url: str
    governing_statute: str              # primary MH practice statute
    statute_url: str

    # Duty to warn / Tarasoff
    duty_to_warn_standard: DutyToWarnStandard
    duty_to_warn_citation: str

    # Mandated reporting (child abuse / dependent-adult / elder)
    mandated_reporter_scope: MandatedReporterScope
    child_abuse_scr_window_hours: int   # hours to file with SCR (24 typical)
    mandated_report_citation: str

    # Civil commitment (involuntary evaluation/treatment)
    civil_commitment_standard: str      # e.g. "danger to self/others, gravely disabled"
    civil_commitment_citation: str

    # 42 CFR Part 2 (federal SUD-record heightened protection)
    part2_applies: bool                 # True in every state (federal)
    part2_state_consistent: bool        # state law permits Part 2 re-disclosure conditions

    # Psychotherapy notes (HIPAA 45 CFR §164.508 — specific authorization)
    psychotherapy_note_specific_auth: bool   # True in every state (HIPAA floor)

    # Minor consent for outpatient MH
    minor_mh_consent_age: int           # minimum age to self-consent to outpatient MH
    minor_mh_consent_citation: str
    minor_mh_parent_access_restricted: bool

    # Record retention (MH records follow the medical retention floor)
    record_retention_adult_years: int
    record_retention_minor_years: int
    record_retention_citation: str

    # Data security (reuses the medical vertical's tier model)
    data_security_citation: str
    breach_notification_days: int

    # --- optional / defaulted fields below ---
    duty_to_warn_note: str = ""
    # Filled from the 50-state + DC duty table. Empty only if a profile
    # predates that table; every current profile sets these.
    duty_classification: str = ""
    duty_trigger: str = ""
    duty_discharge: str = ""
    duty_professions: str = ""
    duty_source_url: str = ""
    duty_checked_on: str = ""
    duty_verified: bool = False
    part2_citation: str = "42 CFR Part 2"
    psychotherapy_note_citation: str = "45 CFR §164.508"
    confidence: str = "established_knowledge"

# ---------------------------------------------------------------------------
# Per-state profiles — 13-state registry (FL, GA, SC, TN, VA, WV, MD, PA,
# OH, NJ, NY, CT, MA), plus CA for the codified-duty eval. Duty-to-warn
# fields come from the researched table. NOT LEGAL OR CLINICAL ADVICE.
# ---------------------------------------------------------------------------

def _duty_kwargs(state: str) -> dict:
    """Profile fields taken from the researched duty-to-warn row.

    California keeps the historical ``tarasoff_codified`` label so the
    existing eval and tests still see that standard. Every other mandatory
    statutory duty uses ``duty_to_protect``, which the crisis gate already
    treats as duty-triggering.
    """
    entry = get_duty_to_warn(state)
    if entry is None:
        raise KeyError(state)
    standard_by_class: dict[str, DutyToWarnStandard] = {
        "mandatory_duty": "duty_to_protect",
        "case_law_only": "tarasoff_common_law",
        "permissive_disclosure": "permissive_disclosure",
        "no_duty_or_none_found": "no_statutory_duty",
    }
    standard: DutyToWarnStandard = (
        "tarasoff_codified" if state == "CA" else standard_by_class[entry.classification]
    )
    return {
        "duty_to_warn_standard": standard,
        "duty_to_warn_citation": entry.citation,
        "duty_to_warn_note": entry.note,
        "duty_classification": entry.classification,
        "duty_trigger": entry.trigger,
        "duty_discharge": entry.discharge,
        "duty_professions": entry.professions,
        "duty_source_url": entry.source_url,
        "duty_checked_on": entry.checked_on,
        "duty_verified": entry.verified,
    }


_FL = MhProfile(
    state="FL", state_name="Florida",
    board_name="FL Board of Clinical Social Work, Marriage & Family Therapy, and Mental Health Counseling",
    board_url="https://floridasmentalhealthprofessions.gov/",
    governing_statute="FL Stat. ch. 491 (Clinical, Counseling, and Psychotherapy Services)",
    statute_url="http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0491/",
    **_duty_kwargs("FL"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="FL Stat. §39.201 (reports of child abuse)",
    civil_commitment_standard="danger to self/others, inability to care for self (Baker Act)",
    civil_commitment_citation="FL Stat. ch. 394 (Baker Act)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=13, minor_mh_consent_citation="FL Stat. §394.4784 (minor may consent to outpatient MH age 13+)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="FL Stat. §456.44 (medical record retention)",
    data_security_citation="FL Stat. §501.171 (breach notification)",
    breach_notification_days=30,
)

_GA = MhProfile(
    state="GA", state_name="Georgia",
    board_name="GA Composite Board of Professional Counselors, Social Workers, and Marriage & Family Therapists",
    board_url="https://sos.ga.gov/georgia-consumer-services/composite-board-professional-counselors-social-workers-and-marriage-family-therapists",
    governing_statute="O.C.G.A. tit. 43, ch. 10A (Professions and Businesses; Counselors, Social Workers, MFTs)",
    statute_url="https://codes.findlaw.com/ga/title-43/ga-st-sect-43-10a-1/",
    **_duty_kwargs("GA"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="O.C.G.A. §19-7-5 (mandated reporters of child abuse)",
    civil_commitment_standard="imminent danger to self/others, gravely disabled",
    civil_commitment_citation="O.C.G.A. §37-3 (Mental Health)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=13, minor_mh_consent_citation="O.C.G.A. §31-12-11 (minor consent for MH/SUD treatment)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="O.C.G.A. §31-33-2 (record retention)",
    data_security_citation="O.C.G.A. §39-1-2 (breach notification)",
    breach_notification_days=30,
)

_SC = MhProfile(
    state="SC", state_name="South Carolina",
    board_name="SC Board of Social Work Examiners / LLR (MH professions)",
    board_url="https://llr.sc.gov/socialwork/",
    governing_statute="S.C. Code tit. 40, ch. 63 (Social Workers); ch. 49 (Counselors/MFTs)",
    statute_url="https://www.scstatehouse.gov/code/t40c63.php",
    **_duty_kwargs("SC"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="S.C. Code §63-7-310 (mandated reporters)",
    civil_commitment_standard="danger to self/others, incapacity",
    civil_commitment_citation="S.C. Code §44-17-410 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="S.C. Code §44-22-100 (minor may consent to MH treatment age 16; outpatient 14 with conditions)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="S.C. Code §44-115-80",
    data_security_citation="S.C. Code §39-1-75 (breach notification)",
    breach_notification_days=30,
)

_TN = MhProfile(
    state="TN", state_name="Tennessee",
    board_name="TN Board of Social Worker Licensure / Health Related Boards",
    board_url="https://www.tn.gov/health/health-program-areas/health-professions/social-worker.html",
    governing_statute="T.C.A. tit. 63, ch. 23 (Social Workers); ch. 22 (Professional Counselors/MFTs)",
    statute_url="https://law.justia.com/codes/tennessee/title-63/",
    **_duty_kwargs("TN"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="T.C.A. §37-1-403 (mandatory reporting)",
    civil_commitment_standard="substantial risk of harm to self/others",
    civil_commitment_citation="T.C.A. §33-6-501 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=13, minor_mh_consent_citation="T.C.A. §33-3-102 (minor consent for MH/SUD)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=7, record_retention_minor_years=7,
    record_retention_citation="T.C.A. §68-11-305",
    data_security_citation="T.C.A. §47-18-2117 (breach notification)",
    breach_notification_days=45,
)

_VA = MhProfile(
    state="VA", state_name="Virginia",
    board_name="VA Board of Counseling / Department of Health Professions",
    board_url="https://www.dhp.virginia.gov/counseling/",
    governing_statute="Va. Code tit. 54.1, ch. 35 (Counselors); ch. 37 (Social Workers)",
    statute_url="https://law.lis.virginia.gov/vacode/title54.1/",
    **_duty_kwargs("VA"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="Va. Code §63.2-1509 (mandatory reporting)",
    civil_commitment_standard="imminent danger to self/others, incapacity",
    civil_commitment_citation="Va. Code §37.2-800 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="Va. Code §54.1-2969 (minor consent for MH treatment age 14+)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=6, record_retention_minor_years=3,
    record_retention_citation="Va. Code §8.01-413",
    data_security_citation="Va. Code §18.2-186.6 (breach notification)",
    breach_notification_days=30,
)

_WV = MhProfile(
    state="WV", state_name="West Virginia",
    board_name="WV Board of Social Work Examiners / Counseling/MFT boards",
    board_url="https://wvswboard.wv.gov/",
    governing_statute="W. Va. Code ch. 30, art. 30 (Social Workers); art. 31 (Counselors); art. 56 (MFTs)",
    statute_url="http://www.wvlegislature.gov/wvcode/",
    **_duty_kwargs("WV"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="W. Va. Code §49-1-209 (mandatory reporting)",
    civil_commitment_standard="imminent danger to self/others, gravely disabled",
    civil_commitment_citation="W. Va. Code §27-5-1 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="W. Va. Code §16-49-3 (minor consent for MH/SUD)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="W. Va. Code §30-3-16",
    data_security_citation="W. Va. Code §46A-2-125 (breach notification)",
    breach_notification_days=30,
)

_MD = MhProfile(
    state="MD", state_name="Maryland",
    board_name="MD Board of Social Work Examiners / Board of Professional Counselors & Therapists",
    board_url="https://health.maryland.gov/socwork/",
    governing_statute="Md. Code, Health Occ. tit. 17 (Professional Counselors/Therapists); tit. 12 (Social Workers)",
    statute_url="https://mgaleg.maryland.gov/megafile_msps/syber/heal/17.htm",
    **_duty_kwargs("MD"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="Md. Code, FL §5-704 (mandatory reporting of child abuse)",
    civil_commitment_standard="danger to self/others, inability to care for self",
    civil_commitment_citation="Md. Code, Health-Gen. §10-617 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="Md. Code, Health-Gen. §20-105 (minor consent for MH/SUD age 16; outpatient 14 per case-law)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="Md. Code, Health-Gen. §4-405",
    data_security_citation="Md. Code, Com. Law §14-3504 (breach notification)",
    breach_notification_days=45,
)

_PA = MhProfile(
    state="PA", state_name="Pennsylvania",
    board_name="PA State Board of Social Workers, Marriage & Family Therapists, and Professional Counselors",
    board_url="https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/SocialWorkersMFTsProfessionalCounselors/",
    governing_statute="63 P.S. §1501 et seq. (Social Workers, MFTs, Professional Counselors)",
    statute_url="https://www.legis.state.pa.us/cfdocs/legis/LI/uactCheck.cfm?txtType=HTM&yr=1987&sessInd=0&act=79",
    **_duty_kwargs("PA"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="23 Pa.C.S. §6311 (mandated reporters)",
    civil_commitment_standard="clear and present danger to self/others",
    civil_commitment_citation="50 P.S. §7301 et seq. (Mental Health Procedures Act)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="50 P.S. §7203 (minor consent for MH treatment age 14+)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=7, record_retention_minor_years=21,
    record_retention_citation="50 P.S. §7111",
    data_security_citation="73 P.S. §2301 (breach notification)",
    breach_notification_days=60,
)

_OH = MhProfile(
    state="OH", state_name="Ohio",
    board_name="OH Counselor, Social Worker, and Marriage & Family Therapist Board",
    board_url="https://cswmft.ohio.gov/",
    governing_statute="Ohio Rev. Code ch. 4757 (Counselors, Social Workers, MFTs)",
    statute_url="https://codes.ohio.gov/ohio-revised-code/chapter-4757",
    **_duty_kwargs("OH"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="Ohio Rev. Code §2151.421 (mandatory reporting)",
    civil_commitment_standard="imminent danger to self/others, incapacity",
    civil_commitment_citation="Ohio Rev. Code §5122.10 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="Ohio Rev. Code §5122.04 (minor consent for MH treatment age 14+)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=5, record_retention_minor_years=7,
    record_retention_citation="Ohio Rev. Code §5122.01",
    data_security_citation="Ohio Rev. Code §1347.12 (breach notification)",
    breach_notification_days=45,
)

_NJ = MhProfile(
    state="NJ", state_name="New Jersey",
    board_name="NJ State Board of Social Work Examiners / Board of Marriage & Family Therapy Examiners",
    board_url="https://www.njconsumeraffairs.gov/sow/",
    governing_statute="N.J.S.A. 45:15BB-1 et seq. (Social Workers); 45:16BB-1 et seq. (MFTs)",
    statute_url="https://www.njconsumeraffairs.gov/sow/Pages/statutes-rules.aspx",
    **_duty_kwargs("NJ"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="N.J.S.A. 9:6-8.10 (mandatory reporting of child abuse)",
    civil_commitment_standard="imminent danger to self/others, inability to care for self",
    civil_commitment_citation="N.J.S.A. 30:4-27.1 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="N.J.S.A. 30:4-77.2 (minor consent for MH treatment age 14+)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=6, record_retention_minor_years=21,
    record_retention_citation="N.J.A.C. 13:44D-5.1",
    data_security_citation="N.J.S.A. 56:8-163 (breach notification)",
    breach_notification_days=30,
)

_NY = MhProfile(
    state="NY", state_name="New York",
    board_name="NYSED Office of the Professions (Social Work; Mental Health Practitioner licensing)",
    board_url="https://www.op.nysed.gov/professions/social-work",
    governing_statute="N.Y. Educ. Law art. 154 (Social Work); art. 163 (Mental Health Practitioners)",
    statute_url="https://www.nysenate.gov/legislation/laws/edn/a154",
    **_duty_kwargs("NY"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="N.Y. Soc. Serv. Law §413 (mandatory reporters)",
    civil_commitment_standard="likelihood of serious harm to self/others, inability to care",
    civil_commitment_citation="N.Y. Mental Hyg. Law §9.39 (emergency admission)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="N.Y. Mental Hyg. Law §33.21 (minor consent for MH/SUD age 14+, outpatient 6 months)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=6, record_retention_minor_years=21,
    record_retention_citation="N.Y. Pub. Health Law §18",
    data_security_citation="N.Y. Gen. Bus. Law §899-aa (SHIELD Act)",
    breach_notification_days=0,
)

_CT = MhProfile(
    state="CT", state_name="Connecticut",
    board_name="CT Department of Public Health (Social Work; Counseling; MFT licensure)",
    board_url="https://portal.ct.gov/dph",
    governing_statute="Conn. Gen. Stat. ch. 383 (Social Workers); ch. 383b (Counselors/MFTs)",
    statute_url="https://www.cga.ct.gov/current/pub/chap_383.htm",
    **_duty_kwargs("CT"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="Conn. Gen. Stat. §17a-101 (mandated reporters)",
    civil_commitment_standard="danger to self/others, psychiatric disability, incapacity",
    civil_commitment_citation="Conn. Gen. Stat. §17a-498 et seq.",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="Conn. Gen. Stat. §19a-14c (minor consent for MH treatment age 14+, 6 sessions)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=6, record_retention_minor_years=21,
    record_retention_citation="Conn. Gen. Stat. §20-7c",
    data_security_citation="Conn. Gen. Stat. §36a-701b (breach notification)",
    breach_notification_days=60,
)

_MA = MhProfile(
    state="MA", state_name="Massachusetts",
    board_name="MA Board of Registration of Social Workers / Allied Mental Health & Human Services Professions",
    board_url="https://www.mass.gov/orgs/board-of-registration-of-social-workers",
    governing_statute="M.G.L. c. 112, §§129A-135 (Allied MH professions); c. 112 §132 (Social Workers)",
    statute_url="https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter112",
    **_duty_kwargs("MA"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=24,
    mandated_report_citation="M.G.L. c. 119, §51A (mandated reporters of child abuse)",
    civil_commitment_standard="likelihood of serious harm to self/others",
    civil_commitment_citation="M.G.L. c. 123, §§7-12 (involuntary commitment)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=14, minor_mh_consent_citation="M.G.L. c. 112, §12F (minor consent for MH treatment age 14+, outpatient, 8 sessions)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=7, record_retention_minor_years=21,
    record_retention_citation="M.G.L. c. 112, §12CC",
    data_security_citation="201 CMR 17.00 (WISP)",
    breach_notification_days=30,
)

# Special Tarasoff-codified profile (CA-style) for the duty-to-warn eval case.
# CA is outside the 13-state registry but the eval needs a codified-duty state
# to prove the gate fires; carried here so the gate module is testable without
# weakening any real-state profile.
_CA = MhProfile(
    state="CA", state_name="California",
    board_name="CA Board of Behavioral Sciences (BBS)",
    board_url="https://www.bbs.ca.gov/",
    governing_statute="Cal. Bus. & Prof. Code §4980 et seq. (MFTs, LCSWs, LPCCs)",
    statute_url="https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=BPC&division=2.&title=&part=&chapter=13.&article=",
    **_duty_kwargs("CA"),
    mandated_reporter_scope="all_clinicians",
    child_abuse_scr_window_hours=36,
    mandated_report_citation="Cal. Penal Code §11164 (mandated reporters)",
    civil_commitment_standard="danger to self/others, gravely disabled",
    civil_commitment_citation="Cal. Welf. & Inst. Code §5150 (LPS Act)",
    part2_applies=True, part2_state_consistent=True,
    psychotherapy_note_specific_auth=True,
    minor_mh_consent_age=12, minor_mh_consent_citation="Cal. Fam. Code §6924 (minor consent for MH treatment age 12+, outpatient)",
    minor_mh_parent_access_restricted=True,
    record_retention_adult_years=7, record_retention_minor_years=21,
    record_retention_citation="17 CCR §1815.5 (MH record retention)",
    data_security_citation="Cal. Civ. Code §1798.82 (breach notification)",
    breach_notification_days=15,
)


_PROFILES: dict[str, MhProfile] = {
    "FL": _FL, "GA": _GA, "SC": _SC, "TN": _TN, "VA": _VA, "WV": _WV,
    "MD": _MD, "PA": _PA, "OH": _OH, "NJ": _NJ, "NY": _NY, "CT": _CT,
    "MA": _MA, "CA": _CA,
}

_13_STATES = ("FL", "GA", "SC", "TN", "VA", "WV", "MD", "PA",
              "OH", "NJ", "NY", "CT", "MA")


def get_mh_profile(state: str) -> MhProfile | None:
    """Return the :class:`MhProfile` for ``state`` (case-insensitive) or None."""
    if not state:
        return None
    return _PROFILES.get(state.upper())


def registered_mh_states() -> tuple[str, ...]:
    """The 13-state MBH registry (FL..MA), in registration order."""
    return _13_STATES


def mh_summary() -> list[dict]:
    """Compact per-state summary for dashboards."""
    out: list[dict] = []
    for st in _13_STATES:
        p = _PROFILES[st]
        out.append({
            "state": p.state,
            "duty_to_warn": p.duty_to_warn_standard,
            "scr_window_h": p.child_abuse_scr_window_hours,
            "minor_mh_age": p.minor_mh_consent_age,
            "part2": p.part2_applies,
            "retention_adult_yr": p.record_retention_adult_years,
        })
    return out


__all__ = [
    "NOT_LEGAL_ADVICE",
    "DutyToWarnEntry",
    "DutyToWarnStandard",
    "MhProfile",
    "all_duty_to_warn",
    "get_duty_to_warn",
    "get_mh_profile",
    "mh_summary",
    "registered_mh_states",
]
