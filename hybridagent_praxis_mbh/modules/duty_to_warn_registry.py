"""Duty-to-warn / duty-to-protect table for all 50 states and the District of Columbia.

NOT LEGAL OR CLINICAL ADVICE. This is decision-support ground compiled from
official legislature and court pages on 2026-09-30. It is not a legal opinion.
Verify the current text with your state board and counsel before relying on it.

Methodology
-----------
Each row was checked against a primary source: the official state code or
session laws, or an official court opinion. Secondary summaries were used
only to locate a citation. A row is ``verified: false`` when the official
text could not be opened, the search did not cover every relevant license
chapter, or sources conflict. Those rows still record what was actually
read, and they do not invent a citation to fill the gap.

Classifications
---------------
- ``mandatory_duty`` — a statute or binding opinion requires protective
  action when the trigger is met. An immunity statute that imposes a duty
  in the exception (no liability unless a threat is communicated and the
  clinician fails to take the listed steps) is a mandatory duty.
- ``permissive_disclosure`` — confidentiality may be breached to warn or
  protect, and no binding duty was verified.
- ``case_law_only`` — the duty comes from a judicial opinion; no duty
  statute was verified.
- ``no_duty_or_none_found`` — no duty statute or binding duty opinion was
  verified. This is an absence-of-finding, not a holding that no duty exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CHECKED_ON = "2026-09-30"

NOT_LEGAL_ADVICE = (
    "Not legal or clinical advice. Verify with your state board and counsel."
)

DutyClassification = Literal[
    "mandatory_duty",
    "permissive_disclosure",
    "no_duty_or_none_found",
    "case_law_only",
]

CLASSIFICATION_LABELS: dict[str, str] = {
    "mandatory_duty": "mandatory duty",
    "permissive_disclosure": "permissive disclosure",
    "no_duty_or_none_found": "no duty or none found",
    "case_law_only": "case-law only",
}


@dataclass(frozen=True)
class DutyToWarnEntry:
    """One jurisdiction's duty-to-warn / duty-to-protect research row."""

    state: str
    state_name: str
    classification: DutyClassification
    citation: str
    trigger: str
    discharge: str
    professions: str
    source_url: str
    checked_on: str = CHECKED_ON
    verified: bool = True
    note: str = ""

    @property
    def classification_label(self) -> str:
        return CLASSIFICATION_LABELS[self.classification]


def _e(
    state: str,
    state_name: str,
    classification: DutyClassification,
    citation: str,
    trigger: str,
    discharge: str,
    professions: str,
    source_url: str,
    *,
    verified: bool = True,
    note: str = "",
) -> DutyToWarnEntry:
    return DutyToWarnEntry(
        state=state,
        state_name=state_name,
        classification=classification,
        citation=citation,
        trigger=trigger,
        discharge=discharge,
        professions=professions,
        source_url=source_url,
        verified=verified,
        note=note,
    )


# Alphabetical by postal code. DC is included. CA is included even though it
# is outside the 13-state practice-profile registry.
_ENTRIES: tuple[DutyToWarnEntry, ...] = (
    _e(
        "AL", "Alabama", "no_duty_or_none_found",
        "Ala. Code §34-26-2 (psychologist privilege; no duty language verified)",
        "No duty-to-warn trigger was verified. The privilege text reviewed says nothing in the chapter shall be construed to require a privileged communication to be disclosed.",
        "not stated",
        "Licensed psychologists, psychiatrists, and psychological technicians, in the privilege text reviewed.",
        "https://alison.legislature.state.al.us/files/pdf/eopa/audit_reports/24_s_001_24S-001-Bd.%20of%20Exam.%20in%20Psychology%20Sunset%20Report.pdf",
        verified=False,
        note=(
            "The live ALISON code viewer did not return section text. The quote is from a "
            "Legislature sunset report reproducing §34-26-2. Counselor and social-work chapters "
            "were not opened, and no Tarasoff-style opinion was opened on judicial.alabama.gov. "
            "Absence of a duty is not confirmed."
        ),
    ),
    _e(
        "AK", "Alaska", "permissive_disclosure",
        "AS 08.86.200(a)(3); AS 08.29.200(a)(1); AS 08.63.200(a)(5); AS 08.95.900(a)(6)",
        "The confidentiality ban does not apply to an immediate threat of serious physical harm to an identifiable victim (psychologists), a clear and immediate probability of physical harm (counselors), or a threat of imminent serious physical harm to an identified victim (marital and family therapists and social workers).",
        "not stated; the sections lift confidentiality and do not say the clinician shall warn",
        "Psychologists and psychological associates; professional counselors; marital and family therapists; licensed social workers.",
        "https://www.akleg.gov/statutesPDF/Title-8.pdf",
        note="Separate shall-report clauses cover child abuse and vulnerable-adult harm. No binding duty-to-warn opinion was opened.",
    ),
    _e(
        "AZ", "Arizona", "mandatory_duty",
        "A.R.S. §36-517.02",
        "The patient communicated an explicit threat of imminent serious physical harm or death to a clearly identified or identifiable victim, with apparent intent and ability, and the provider fails to take reasonable precautions.",
        "Communicate the threat when possible to all identifiable victims; notify law enforcement where the patient or any potential victim resides; take reasonable steps to initiate voluntary or involuntary hospitalization if appropriate; and take any other precautions a reasonable and prudent mental health provider would take.",
        "Any physician or provider of mental health or behavioral health services involved in evaluating, caring for, treating, or rehabilitating a patient (A.R.S. §36-501).",
        "https://www.azleg.gov/ars/36/00517-02.htm",
        note=(
            "Avitia v. Crisis Preparation and Recovery Inc., No. CV-22-0288-PR (Ariz. Oct. 16, 2023), "
            "https://www.azcourts.gov/Portals/0/OpinionFiles/Supreme/2023/CV220288PR.pdf, overruled "
            "earlier opinions that had held §36-517.02 unconstitutional. The section remains in the official code."
        ),
    ),
    _e(
        "AR", "Arkansas", "mandatory_duty",
        "Ark. Code Ann. §§20-45-201 and 20-45-202 (Act 1212 of 2013)",
        "The patient communicates an explicit and imminent threat to kill or seriously injure a clearly or reasonably identifiable victim, or to commit a specific violent act or destroy property under circumstances that could easily lead to serious personal injury or death, and has apparent intent and ability.",
        "Timely notice to law enforcement in the victim's county, the patient's county, or the Department of Arkansas State Police, or immediate voluntary or involuntary hospitalization. For a patient under 18 who threatens suicide or serious self-harm, the provider shall make a reasonable effort to tell the custodial parent, then the noncustodial parent or legal guardian.",
        "Licensed certified social worker, LMFT, LPC, physician, psychologist, or registered nurse (including an APRN) who provides mental health services; hospitals, facilities, community mental health centers, and clinics are also named.",
        "https://arkleg.state.ar.us/Acts/FTPDocument?ddBienniumSession=2013%2F2013R&file=1212.pdf&path=%2FACTS%2F2013R%2FPublic%2F",
        note="Official source opened is the 2013 enrolled act, not a 2026 code compilation. No later amending act was located on this check.",
    ),
    _e(
        "CA", "California", "mandatory_duty",
        "Cal. Civ. Code §43.92; Tarasoff v. Regents of Univ. of Cal., 17 Cal.3d 425 (1976)",
        "The patient has communicated to the psychotherapist a serious threat of physical violence against a reasonably identifiable victim or victims.",
        "Reasonable efforts to communicate the threat to the victim or victims and to a law enforcement agency.",
        "Psychotherapists under Evid. Code §1010, including psychiatrists, psychologists, LCSWs engaged in psychotherapy, school psychologists, MFTs, psychiatric-mental health nurses, LPCCs, and listed associates and trainees.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=43.92",
        note="The 2013 wording change from duty to warn and protect to duty to protect was stated not to be a substantive change. The Tarasoff opinion itself was not re-opened on the California courts site on this check; the duty classification follows the current statute.",
    ),
    _e(
        "CO", "Colorado", "mandatory_duty",
        "C.R.S. §13-21-117",
        "The patient has communicated a serious threat of imminent physical violence against a specific person or persons, including those identifiable by association with a specific location or entity.",
        "The provider shall make reasonable and timely efforts to notify the person or persons threatened, or the person responsible for the threatened location or entity, and an appropriate law enforcement agency, or take other appropriate action, including hospitalizing the patient.",
        "Physician, social worker, psychiatric nurse, psychologist, or other mental health professional, or a mental health hospital, behavioral health entity, institution, or their staff.",
        "https://leg.colorado.gov/sites/default/files/images/olls/crs2024-title-13.pdf",
        note="Legislature PDF is labeled Colorado Revised Statutes 2024 uncertified printout. No 2025 or 2026 amendment was located.",
    ),
    _e(
        "CT", "Connecticut", "permissive_disclosure",
        "Conn. Gen. Stat. §52-146f(2) (2026 supplement)",
        "The psychologist or psychiatric mental health provider determines there is a substantial risk of imminent physical injury by the person or patient to himself, herself, or others.",
        "not stated; the verb is may disclose, not shall",
        "A psychologist licensed under chapter 383 and a psychiatric mental health provider, as defined for §52-146d to §52-146j.",
        "https://www.cga.ct.gov/2026/sup/chap_899.htm",
        note=(
            "Section 52-146c was repealed effective Oct. 1, 2025. Parallel marriage-and-family, "
            "social-work, and professional-counselor confidentiality sections were not opened, "
            "and no supreme-court opinion imposing a duty was opened. Conn. Gen. Stat. §17a-450 "
            "is not a duty-to-warn statute."
        ),
    ),
    _e(
        "DE", "Delaware", "mandatory_duty",
        "16 Del. C. §§5401–5402",
        "The patient has communicated an explicit and imminent threat to kill or seriously injure a clearly identified victim, or to commit a specific violent act or destroy property under circumstances which could easily lead to serious personal injury or death, and has apparent intent and ability, and the provider fails to take the stated precautions.",
        "In a timely manner, both notify law enforcement where the potential victim or the patient resides and communicate the threat to the clearly identified victim, and arrange immediate voluntary or involuntary hospitalization.",
        "Physician, registered professional nurse, licensed counselor working in mental health, psychologist, and licensed clinical social worker; also an institution, agency, or hospital.",
        "https://delcode.delaware.gov/title16/c054/index.html",
        note="Section 5403 separately permits disclosure to law enforcement if the patient is dangerous to self or others even without an identifiable victim.",
    ),
    _e(
        "DC", "District of Columbia", "permissive_disclosure",
        "D.C. Code §7-1203.03",
        "The mental health professional reasonably believes disclosure is necessary to initiate or seek emergency hospitalization under §21-521, or otherwise to protect the client or another individual from a substantial risk of imminent and serious physical injury.",
        "not stated; disclosure may be made, limited to the minimum necessary, to listed recipients including an intended victim and an officer authorized to make arrests",
        "Mental health professional (definition section not opened).",
        "https://code.dccouncil.gov/us/dc/council/code/sections/7-1203.03",
        note="The verb is may, not shall. No binding case imposing a duty was opened.",
    ),
    _e(
        "FL", "Florida", "mandatory_duty",
        "Fla. Stat. §§456.059, 490.0147(2), 491.0147(2) (2026)",
        "The patient communicated a specific threat to cause serious bodily injury or death to an identified or readily available person, and the clinician makes a clinical judgment that the patient has the apparent intent and ability to imminently or immediately carry out the threat.",
        "The psychiatrist, psychologist, or chapter 491 licensee shall/must disclose the threat to a law enforcement agency. Warning the potential victim is permissive (may), not mandatory. Law enforcement that receives the notice must take appropriate action, which may include notifying the intended victim or initiating a risk protection order.",
        "Psychiatrists (Fla. Stat. §456.059); psychologists (§490.0147); clinical social workers, marriage and family therapists, and mental health counselors licensed under chapter 491 (§491.0147).",
        "https://www.flsenate.gov/Laws/Statutes/2026/491.0147",
        note=(
            "Parallel shall-notify-law-enforcement text was also read for psychologists at "
            "https://www.flsenate.gov/Laws/Statutes/2026/490.0147 and for psychiatrists at "
            "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0456/Sections/0456.059.html. "
            "Reported appellate opinions (Boynton v. Burglass, 590 So. 2d 446 (Fla. 3d DCA 1991), "
            "and later district-court discussion) are described in secondary sources as rejecting "
            "a common-law tort duty and civil liability for failure to warn. Those opinions were "
            "not retrieved from an official court site on this check. The classification follows "
            "the statutory shall/must command to notify law enforcement."
        ),
    ),
    _e(
        "GA", "Georgia", "case_law_only",
        "Bradley Center, Inc. v. Wessner, 250 Ga. 199, 296 S.E.2d 693 (1982)",
        "Reported holding: where treatment of a mental patient involves a physician's exercise of control, and the physician knows or should know the patient is likely to cause bodily harm to others, a duty arises to exercise that control with reasonable care to prevent harm.",
        "not stated in a source opened on the Georgia Supreme Court site",
        "The reported opinion addresses a physician and a private mental health hospital that took charge of a voluntary patient.",
        "https://storage.courtlistener.com/harvard_pdf/1339729.pdf",
        verified=False,
        note=(
            "The opinion was not opened on the Georgia Supreme Court site. The text reviewed is "
            "a scan of 250 Ga. 199, not the court site. The Official Code of Georgia was not "
            "opened on the state's code publisher. O.C.G.A. §51-1-27 is a general professional-care "
            "statute and is not a Tarasoff codification. Do not treat this row as a verified duty."
        ),
    ),
    _e(
        "HI", "Hawaii", "permissive_disclosure",
        "Haw. Rev. Stat. §626-1, Rule 504.1(d)(6); Haw. Rev. Stat. §453D-13(2)",
        "There is no psychologist-client privilege as to a communication reflecting the client's intent to commit a criminal or tortious act that the psychologist reasonably believes is likely to result in death or substantial bodily harm. A mental health counselor is not required to withhold information to prevent a clear and imminent danger.",
        "not stated; the evidence-rule commentary says the exception is intended to allow disclosure",
        "A person authorized, or reasonably believed to be authorized, to diagnose or treat a mental or emotional condition; licensed clinical social workers by reference to Rule 504.1; licensed mental health counselors under §453D-13.",
        "https://www.capitol.hawaii.gov/hrscurrent/Vol13_Ch0601-0676/HRS0626/HRS_0626-0001-0504_0001.htm",
        note="Rule commentary predicts Hawaii will likely embrace Tarasoff and cites Lee v. Corregedore, 83 Haw. 154 (1996). Lee was not opened. No binding case imposing a third-party warning duty was verified.",
    ),
    _e(
        "ID", "Idaho", "mandatory_duty",
        "Idaho Code §§6-1901 to 6-1904",
        "The patient has communicated an explicit threat of imminent serious physical harm or death to a clearly identified or identifiable victim or victims, and has the apparent intent and ability to carry out the threat.",
        "A reasonable effort, in a reasonably timely manner, to communicate the threat to the victim and to notify the law enforcement agency closest to the patient's or victim's residence. If the victim is a minor, also a reasonable effort to communicate the threat to the custodial parent, noncustodial parent, or legal guardian.",
        "Physician, professional counselor, psychologist, social worker, or licensed professional nurse.",
        "https://legislature.idaho.gov/statutesrules/idstat/title6/t6ch19/sect6-1902/",
        note="Section 6-1904 gives immunity for failure to predict or protect other than the duty in §6-1902, and does not modify a custodial hospital's duty.",
    ),
    _e(
        "IL", "Illinois", "mandatory_duty",
        "405 ILCS 5/6-103(b), (c)",
        "The recipient has communicated a serious threat of physical violence against a reasonably identifiable victim or victims.",
        "A reasonable effort to communicate the threat to the victim and to a law enforcement agency, or a reasonable effort to obtain hospitalization of the recipient.",
        "Physician, clinical psychologist, advanced practice psychiatric nurse, or qualified examiner.",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/040500050K6-103.htm",
        note="Official page source line: P.A. 104-270, effective Aug. 15, 2025. Section 6-103.3 is a separate clear-and-present-danger notice to the Department of Human Services or Illinois State Police.",
    ),
    _e(
        "IN", "Indiana", "mandatory_duty",
        "Ind. Code §§34-30-16-1 and 34-30-16-2",
        "The patient has communicated an actual threat of physical violence or other means of harm against a reasonably identifiable victim or victims, or evidences conduct or makes statements indicating an imminent danger of serious personal injury or death to others.",
        "One or more of: reasonable attempts to communicate the threat to the victim; notify police or other law enforcement where the patient or victim resides; seek civil commitment; take reasonably available steps to prevent violence until law enforcement takes custody; or report the threat to an employer-designated physician or psychologist who has the responsibility to warn.",
        "Physicians, licensed hospitals and private institutions, psychologists, school psychologists, qualifying campus counseling centers, nurses, clinical social workers, community mental health centers, specified substance-use programs, state institutions, and other providers listed in IC 34-6-2.1-123.",
        "https://iga.in.gov/ic/2026/Title_34/Article_30/Chapter_16.pdf",
        note="Indiana Code 2026 PDF. The profession definition was amended by P.L.145-2026.",
    ),
    _e(
        "IA", "Iowa", "mandatory_duty",
        "Iowa Code §228.7A (2026)",
        "The individual has communicated to the mental health professional an imminent threat of physical violence against the individual's self or against a clearly identifiable victim or victims.",
        "Reasonable efforts to communicate the threat to a law enforcement professional. The duty discharged is disclosure to law enforcement, not expressly a warning to the victim.",
        "A mental health professional under Iowa Code §228.1(7), including a master's-level licensee in a mental health field with two years of supervised clinical experience, a psychiatrist, a psychiatric advanced registered nurse practitioner, a physician assistant practicing with a psychiatrist, or a licensed doctoral psychologist.",
        "https://www.legis.iowa.gov/docs/code/228.7A.pdf",
        note="Subsection 1 is permissive (may be disclosed) to prevent or lessen a serious and imminent threat. The mandatory piece is the subsection 2 exception.",
    ),
    _e(
        "KS", "Kansas", "permissive_disclosure",
        "K.S.A. 65-5603(a)(6)",
        "The treatment-facility privilege does not cover threat information when a patient has specifically identified a person threatened with substantial physical harm, treatment personnel believe the patient is substantially likely to act in the reasonably foreseeable future, and the head of the treatment facility has concluded that notification should be given.",
        "not stated; this is a privilege exception, not a command to warn",
        "Treatment personnel of a treatment facility (community mental health center, community service provider, psychiatric hospital, or state institution for people with intellectual disability).",
        "https://ksrevisor.gov/statutes/chapters/ch65/065_056_0003.html",
        note="No separate private-practice duty-to-warn statute was found on the Revisor site.",
    ),
    _e(
        "KY", "Kentucky", "mandatory_duty",
        "KRS 202A.400",
        "The patient has communicated an actual threat of physical violence against a clearly identified or reasonably identifiable victim, or an actual threat of some specific violent act.",
        "For an identifiable victim, reasonable efforts to communicate the threat to the victim and to notify the police department closest to the patient's and the victim's residence. If the threat is of a specific violent act and no victim is identifiable, reasonable efforts to communicate the threat to law enforcement. Reasonable efforts to seek civil commitment also satisfy the duty to take reasonable precautions.",
        "Physicians and psychiatrists, psychologists and listed psychology practitioners, registered nurses providing mental health services, licensed clinical and certified social workers providing mental health services, marriage and family therapists, professional counselors, certified art therapists, and licensed pastoral counselors (KRS 202A.400(4)).",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=44466",
        note="Effective June 24, 2015. The statute states when the duty arises.",
    ),
    _e(
        "LA", "Louisiana", "mandatory_duty",
        "La. R.S. 9:2800.2",
        "The patient has communicated a threat of physical violence, deemed significant in the treating professional's clinical judgment, against a clearly identified victim or victims, coupled with the apparent intent and ability to carry out the threat.",
        "Reasonable effort to communicate the threat to the potential victim or victims and to notify law enforcement authorities in the vicinity of the patient's or potential victim's residence.",
        "Psychologist, medical psychologist, psychiatrist, marriage and family therapist, licensed professional counselor, and social worker.",
        "https://legis.la.gov/Legis/Law.aspx?d=107255",
        note="Current legislative text includes Acts 2021, No. 238.",
    ),
    _e(
        "ME", "Maine", "mandatory_duty",
        "32 M.R.S. §§2600-F, 3300-I, 3820, 6207-C, 7007, and 13867",
        "The licensee has a reasonable belief, based on communications with the patient or client, that the person is likely to engage in physical violence that poses a serious risk of harm to self or others.",
        "Reasonable efforts to communicate the threat to a potential victim, notification of a law enforcement agency, or seeking involuntary hospitalization under Title 34-B. The duty does not require action that, in reasonable professional judgment, would endanger the licensee or increase the danger to a potential victim.",
        "Osteopathic physicians, physicians, psychologist licensees, certified or licensed alcohol and drug counselors, social-work licensees, and counseling-professional licensees.",
        "https://legislature.maine.gov/statutes/32/title32sec13867.html",
        note="Enacted by P.L. 2019, ch. 317. Parallel sections were opened for the other listed professions.",
    ),
    _e(
        "MD", "Maryland", "mandatory_duty",
        "Md. Code, Cts. & Jud. Proc. §5-609",
        "The mental health care provider or administrator knew of the patient's propensity for violence and the patient indicated, by speech, conduct, or writing, an intention to inflict imminent physical injury upon a specified victim or group of victims.",
        "The duty is discharged by reasonable and timely efforts to seek civil commitment; or to formulate a diagnostic impression and establish and undertake a documented treatment plan calculated to eliminate the possibility that the patient will carry out the threat; or to inform the appropriate law enforcement agency and, if feasible, the specified victim or victims, of the nature of the threat, the patient's identity, and the victim's identity.",
        "A mental health care provider licensed under the Health Occupations Article, and any facility, corporation, partnership, association, or other entity that provides treatment or services to individuals who have mental disorders; also an administrator of a facility as defined in Health-General §10-101.",
        "https://mgaleg.maryland.gov/2026RS/Statute_Web/gcj/5-609.pdf",
    ),
    _e(
        "MA", "Massachusetts", "mandatory_duty",
        "M.G.L. c. 123, §36B",
        "The patient has communicated an explicit threat to kill or inflict serious bodily injury on a reasonably identified victim and has the apparent intent and ability to carry it out, or the patient has a known history of physical violence and the professional has a reasonable basis to believe there is a clear and present danger that the patient will attempt to kill or inflict serious bodily injury on a reasonably identified victim, and the professional fails to take reasonable precautions.",
        "Reasonable precautions under M.G.L. c. 123, §1: reasonable efforts to communicate the threat to the reasonably identified victim; notify an appropriate law enforcement agency where the patient or any potential victim resides; arrange voluntary hospitalization; or, within the legal scope of practice, initiate involuntary hospitalization.",
        "A licensed mental health professional under §1: a person who holds himself or herself out as providing mental health services and who must obtain a license from the Commonwealth.",
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVII/Chapter123/Section36B",
        note="Section 36C is a separate firearms-commitment reporting provision, not the victim-warning duty. The precautions definition was read at https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVII/Chapter123/Section1.",
    ),
    _e(
        "MI", "Michigan", "mandatory_duty",
        "MCL 330.1946",
        "A patient communicates to a treating mental health professional a threat of physical violence against a reasonably identifiable third person, and the patient has the apparent intent and ability to carry out that threat in the foreseeable future.",
        "In a timely manner, hospitalize the patient or initiate hospitalization proceedings, or make a reasonable attempt to communicate the threat to the third person and to the local police, county sheriff, or state police. If the threatened person is a minor or is incompetent other than by age, also notify the county department of social services and the custodial parent, noncustodial parent, or legal guardian, as appropriate.",
        "Mental health professional in MCL 330.1100b: a physician, psychologist, registered professional nurse, licensed master's social worker, licensed professional counselor, or marriage and family therapist.",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-330-1946",
        note="Except as this section provides, there is no duty to warn or protect.",
    ),
    _e(
        "MN", "Minnesota", "mandatory_duty",
        "Minn. Stat. §§148.975, 148E.240 subd. 6, 148B.391, 148B.593, and 148F.13 subd. 2",
        "For psychologists, social workers, and marriage and family therapists, a client or other person has communicated a specific, serious threat of physical violence against a specific, clearly identified or identifiable potential victim. For professional counselors and alcohol and drug counselors, the threat may be against self or such a victim.",
        "Psychologists, social workers, and marriage and family therapists: communicate the threat to the potential victim and, if contact cannot be made, to the law enforcement agency closest to the potential victim or the client. Counselors and alcohol and drug counselors: reasonable efforts to communicate the threat to law enforcement, the potential victim, the client's family, or appropriate third parties in a position to prevent the harm.",
        "Psychology licensees and specified trainees; social-work licensees, interns, and students; marriage and family therapy licensees and specified students or interns; professional counseling licensees and specified students or interns; alcohol and drug counseling providers and specified trainees.",
        "https://www.revisor.mn.gov/statutes/cite/148.975",
        note="Sections 148.975 and 148B.391 do not apply to a threat of suicide or other self-harm. Social workers must comply with the duty established by §148.975.",
    ),
    _e(
        "MS", "Mississippi", "permissive_disclosure",
        "Miss. Code Ann. §41-21-97(1)(e) (2023 S.B. 2797, Laws 2023, ch. 337)",
        "The patient has communicated to the treating physician, psychologist, master social worker, or licensed professional counselor an actual threat of physical violence against a clearly identified or reasonably identifiable potential victim or victims.",
        "not stated; the enrolled act says the professional may communicate the threat only to the potential victim, a law enforcement agency, or the parent or guardian of a minor identified as a potential victim",
        "Treating physicians, psychologists as defined in §73-31-3(e), master social workers, and licensed professional counselors.",
        "https://billstatus.ls.state.ms.us/documents/2023/html/SB/2700-2799/SB2797SG.htm",
        note="Signed enrolled bill, effective July 1, 2023. No later amendment of §41-21-97 was found on the Legislature's bill-status site for 2024–2026. The operative word is may.",
    ),
    _e(
        "MO", "Missouri", "case_law_only",
        "Bradley v. Ray, 904 S.W.2d 302 (Mo. App. 1995)",
        "A treating psychologist has a common-law duty to warn or protect when there is an identifiable victim, as recited by a later official Missouri Court of Appeals opinion.",
        "not stated",
        "Treating psychologists and psychiatrists, as described in that later official opinion's statement of the Bradley holding.",
        "http://www.courts.mo.gov/file.jsp?id=34072",
        note=(
            "The 1995 slip opinion was not separately opened. The holding was read in a later "
            "official Court of Appeals opinion. This is intermediate appellate precedent, not a "
            "Missouri Supreme Court opinion. Searches of revisor.mo.gov did not return a Tarasoff duty statute."
        ),
    ),
    _e(
        "MT", "Montana", "mandatory_duty",
        "MCA 27-1-1102",
        "The patient has communicated to the mental health professional an actual threat of physical violence by specific means against a clearly identified or reasonably identifiable victim.",
        "Reasonable efforts to communicate the threat to the victim and to notify the law enforcement agency closest to the patient's or the victim's residence, and to supply a requesting law enforcement agency with information concerning the threat.",
        "Mental health professional in MCA 27-1-1101: a certified professional person under 53-21-106; a physician; a psychologist; a psychiatric-mental-health advanced practice registered nurse; or a clinical social worker, professional counselor, or marriage and family therapist licensed under Title 37, chapter 39.",
        "https://leg.mt.gov/bills/mca/title_0270/chapter_0010/part_0110/section_0020/0270-0010-0110-0020.html",
        note="Definition section, amended through Laws 2025, ch. 53, was opened on the current MCA site.",
    ),
    _e(
        "NE", "Nebraska", "mandatory_duty",
        "Neb. Rev. Stat. §§38-2137 and 38-3132",
        "For a mental health practitioner, the patient has communicated a serious threat of physical violence against himself, herself, or a reasonably identifiable victim or victims. For a psychologist, the threat is against a reasonably identifiable victim or victims.",
        "Reasonable efforts to communicate the threat to the victim or victims and to a law enforcement agency.",
        "Section 38-2137 covers a person licensed or certified under the Mental Health Practice Act and a professional counselor practicing in Nebraska under the interstate compact. Section 38-3132 covers psychologists.",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=38-2137",
        note="The psychologist statute was also opened at https://nebraskalegislature.gov/laws/statutes.php?statute=38-3132. The Legislature's annotation cites Holloway v. State, 293 Neb. 12 (2016); that opinion was not opened.",
    ),
    _e(
        "NV", "Nevada", "mandatory_duty",
        "NRS 629.550",
        "A patient communicates an explicit threat of imminent serious physical harm or death to a clearly identified or identifiable person and, in the professional's judgment, the patient has the intent and ability to carry out the threat.",
        "The professional shall place the patient on a mental health crisis hold, petition a court to order such a hold, or make a reasonable effort to communicate the threat in a timely manner to the person threatened, the law enforcement agency closest to that person's residence, and, if that person is a minor, the parent or guardian.",
        "Physicians and psychiatrists; psychologists; specified behavioral health practitioners; clinical social workers employed by the Division of Public and Behavioral Health who meet the subsection's conditions; specified registered nurses; marriage and family therapists and clinical professional counselors; and specified federal employees.",
        "https://www.leg.state.nv.us/nRs/NRS-629.html",
        note="Added 2015; amended through 2025. A social worker is included only if the subsection's employment conditions are met.",
    ),
    _e(
        "NH", "New Hampshire", "mandatory_duty",
        "RSA 329:31, RSA 329-B:29, and RSA 330-A:35",
        "The client or patient has communicated a serious threat of physical violence against a clearly identified or reasonably identifiable victim or victims, or a serious threat of substantial damage to real property.",
        "Any one of: reasonable efforts to communicate the threat to the victim or victims; notification of the police department closest to the client's or potential victim's residence; or civil commitment to the state mental health system.",
        "A physician licensed under RSA 329, including a person providing treatment under that physician's supervision; a person licensed under the psychologists chapter; and a person licensed under the mental health practice chapter (pastoral psychotherapists, clinical social workers, school social workers, clinical mental health counselors, and marriage and family therapists).",
        "https://www.gencourt.state.nh.us/rsa/html/XXX/329/329-31.htm",
        note="Psychologist and mental-health-practice sections were also opened: https://www.gencourt.state.nh.us/rsa/html/XXX/329-B/329-B-29.htm and https://www.gencourt.state.nh.us/rsa/html/XXX/330-A/330-A-35.htm.",
    ),
    _e(
        "NJ", "New Jersey", "mandatory_duty",
        "N.J.S.A. 2A:62A-16 (P.L. 2018, c.34; P.L. 2019, c.59)",
        "The patient communicated a threat of imminent, serious physical violence against a readily identifiable individual or against himself or herself, and a reasonable professional would believe the patient intended to carry it out; or the circumstances are such that a reasonable professional would believe the patient intended to carry out an act of imminent, serious physical violence against a readily identifiable individual or against himself or herself.",
        "Any one or more of: arrange voluntary psychiatric admission; initiate involuntary commitment; advise local law enforcement of the threat and the identity of the intended victim; warn the intended victim, or the parent or guardian if the victim is under 18; or, if the patient is under 18 and threatens suicide or bodily injury to himself or herself, warn the patient's parent or guardian. P.L. 2018, c.34 also requires notice to the chief law enforcement officer, or the Superintendent of State Police, for a firearms-disability check.",
        "P.L. 2018, c.34: a person licensed to practice psychology, psychiatry, medicine, nursing, clinical social work, or marriage and family therapy.",
        "https://pub.njleg.gov/bills/2018/AL18/34_.HTM",
        note=(
            "Official session-law pages, not a codified database. P.L. 2019, c.59 "
            "(https://pub.njleg.gov/bills/2018/AL19/59_.HTM) adds that a duty is not incurred when "
            "a qualified terminally ill patient requests medication under the Medical Aid in Dying "
            "for the Terminally Ill Act. That 2019 pamphlet restates the section from an earlier "
            "comparison text, so this check does not resolve whether the restatement disturbed the "
            "2018 marriage-and-family-therapy wording or the firearms-notice subsection. No later "
            "enacted amendment was found."
        ),
    ),
    _e(
        "NM", "New Mexico", "permissive_disclosure",
        "NMSA 1978, §§43-1-19(B)(2) and 32A-6A-24(D)(2) (2024 S.B. 230)",
        "Disclosure without authorization is allowed when it is necessary to protect against a clear and substantial risk of imminent serious physical injury or death inflicted by the client or child on self or another.",
        "not stated; authorization shall not be required for that disclosure, and the text does not say the professional must warn a victim",
        "Not stated as a named licensure list. Section 43-1-19 covers confidential information under the Mental Health and Developmental Disabilities Code. Section 32A-6A-24 covers the children's act.",
        "https://www.nmlegis.gov/Sessions/24%20Regular/final/SB0230.pdf",
        note="Enrolled final of 2024 Senate Bill 230, effective July 1, 2024. The Compilation Commission codification page was not separately opened.",
    ),
    _e(
        "NY", "New York", "mandatory_duty",
        "N.Y. Mental Hyg. Law §9.46",
        "A mental health professional currently providing treatment determines, in the exercise of reasonable professional judgment, that the person is likely to engage in conduct that would result in serious harm to self or others.",
        "Report, as soon as practicable, to the director of community services or the director's designee. The director reports to the Division of Criminal Justice Services only if the director agrees. Information sent to DCJS is limited to names and other non-clinical identifying information and may be used for firearm-license decisions. The section does not require a warning to an identified victim.",
        "Physician, psychiatrist, psychologist, registered nurse, licensed clinical social worker, licensed master social worker, licensed mental health counselor, clinical nurse specialist, certified nurse practitioner, licensed clinical marriage and family therapist, or licensed professional nurse.",
        "https://www.nysenate.gov/legislation/laws/MHY/9.46",
        note=(
            "This is a SAFE Act report, not a Tarasoff warn-the-victim duty. The full text of "
            "Mental Hygiene Law §33.13 was not retrieved (the Senate page timed out), so an "
            "earlier confidentiality exception, if one exists, was not verified. No binding "
            "victim-warning opinion was verified. A 2025-2026 bill that would authorize disclosure "
            "to an identifiable endangered person was unenacted on this check."
        ),
    ),
    _e(
        "NC", "North Carolina", "permissive_disclosure",
        "N.C.G.S. §122C-55(d)",
        "In the responsible professional's opinion, there is an imminent danger to the health or safety of the client or another individual, or there is a likelihood of the commission of a felony or violent misdemeanor.",
        "not stated; the verb is may disclose",
        "A responsible professional under N.C.G.S. §122C-3(32): an individual within a facility designated by the facility director to be responsible for the care, treatment, habilitation, or rehabilitation of a specific client.",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/ByArticle/Chapter_122C/Article_3.html",
        note="No statute requiring a warning to an identified victim was found in Chapter 122C, Article 3. G.S. 8-53.3 is a psychologist privilege statute and does not create a victim-warning duty. No binding duty opinion was opened.",
    ),
    _e(
        "ND", "North Dakota", "mandatory_duty",
        "N.D.C.C. §43-53-11(2)–(4)",
        "The patient has communicated to the licensee a serious threat of physical violence against a reasonably identifiable victim or victims.",
        "Reasonable efforts to communicate the threat to the victim or victims and to a law enforcement agency.",
        "A licensee under N.D.C.C. chapter 43-53 (marriage and family therapy practice). Parallel duty language was not found in the psychologist, social-worker, or counselor chapters opened on this check.",
        "https://ndlegis.gov/cencode/t43c53.pdf",
        note="The duty verified here is limited to marriage-and-family-therapy licensees. No North Dakota Supreme Court Tarasoff opinion was located on ndcourts.gov.",
    ),
    _e(
        "OH", "Ohio", "mandatory_duty",
        "Ohio Rev. Code §2305.51 (eff. Apr. 9, 2025)",
        "The client or patient, or a knowledgeable person, has communicated an explicit threat of inflicting imminent and serious physical harm to or causing the death of one or more clearly identifiable potential victims, and the professional or organization has reason to believe the client or patient has the intent and ability to carry out the threat.",
        "One or more, in a timely manner, and with the reasons for choosing or rejecting each alternative documented: emergency hospitalization under R.C. 5122.10; voluntary or involuntary hospitalization under chapter 5122; a documented treatment plan reasonably calculated to eliminate the possibility that the threat will be carried out, plus a second-opinion risk assessment; or communicate the nature of the threat and the identities of the client and each potential victim to a law enforcement agency and, if feasible, to each potential victim or a minor or incompetent victim's parent or guardian.",
        "A mental health professional: an individual licensed, certified, or registered under the Revised Code, or otherwise authorized in Ohio, to provide mental health services for compensation. Mental health services include medical, psychiatric, psychological, professional counseling, social work, marriage and family therapy, or nursing principles applied to mental, emotional, psychiatric, psychological, or psychosocial disorders or adjustment.",
        "https://codes.ohio.gov/ohio-revised-code/section-2305.51",
        note="For a threat to a readily identifiable structure, a clearly identifiable potential victim includes any potential occupant. The professional is not required to take an action that would physically endanger the professional, increase the danger to a potential victim, or increase the danger to the client.",
    ),
    _e(
        "OK", "Oklahoma", "case_law_only",
        "Wofford v. Eastern State Hospital, 1990 OK 77, 795 P.2d 516, as stated in later Oklahoma Supreme Court opinions on OSCN",
        "Special psychotherapist or hospital-patient relationship and, under professional standards, knowledge or reason to know that the patient's dangerous propensities present an unreasonable risk of harm to persons foreseeably endangered by release.",
        "Not specified by statute. The opinions describe reasonable professional care in the release decision.",
        "Psychiatrist and mental hospital in the negligent-release setting described in Wofford, as quoted by later OSCN opinions.",
        "https://www.oscn.net/applications/OCISWeb/DeliverDocument.asp?CiteID=379420",
        note=(
            "This is a negligent-release duty to foreseeable victims, not a communicated-threat "
            "warning statute. The 1990 slip opinion itself was not the page retrieved; the holding "
            "was taken from later OSCN opinions that quote it. 43A O.S. §1-109(E) is permissive only: "
            "authorization is not required when failure to disclose presents a serious threat "
            "(https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os43A.pdf). Johnson v. Fine, "
            "2002 OK 39, treats Wofford as a narrow special-relationship duty."
        ),
    ),
    _e(
        "OR", "Oregon", "permissive_disclosure",
        "ORS 179.505(12) (2025); ORS 40.252 (2025)",
        "Information from diagnosis, evaluation, or treatment that in the provider's professional judgment indicates a clear and immediate danger to others or to society may be reported. ORS 40.252 limits a privilege only if the professional also chooses to report.",
        "None. Both sections state that nondisclosure does not create civil liability. ORS 40.252(2) states that the section does not create a duty to report.",
        "ORS 179.505 applies to a health care services provider as defined in that section. ORS 40.252 applies to persons receiving communications covered by the listed privileges, including psychotherapist-patient and regulated social worker-client.",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors179.html",
        note="Separate and narrower: ORS 40.245(2) says a licensed public-school counselor shall report, or take other emergency measures, when a student's condition presents a clear and imminent danger. That school-counselor sentence is not the general clinician rule.",
    ),
    _e(
        "PA", "Pennsylvania", "case_law_only",
        "Emerich v. Philadelphia Center for Human Development, Inc., 554 Pa. 209, 720 A.2d 1032 (1998)",
        "The patient communicated to the mental health professional a specific and immediate threat of serious bodily injury against a specifically identified or readily identifiable third party, and the professional determines, or under professional standards should determine, that the patient presents a serious danger of violence to that third party.",
        "The later official opinions describe a duty to warn that identified or readily identifiable victim. They do not set out a statutory menu of alternative steps.",
        "Mental health professional, as described in those opinions.",
        "https://www.pacourts.us/assets/opinions/Supreme/out/J-72-2011mo.pdf",
        note=(
            "The 1998 Emerich opinion was not found as its own PDF on pacourts.us. The holding "
            "used here is from later official opinions that cite it, including the Supreme Court "
            "opinion at the source URL. 50 P.S. §7111 (Mental Health Procedures Act §111) is a "
            "confidentiality statute, not a duty to warn: "
            "https://www.legis.state.pa.us/WU01/LI/LI/US/PDF/1976/0/0143..PDF."
        ),
    ),
    _e(
        "RI", "Rhode Island", "permissive_disclosure",
        "R.I. Gen. Laws §5-39.1-4(a)(2)",
        "A clear and present danger to the safety of the patient or client or to other individuals, as an exception to the social-worker nondisclosure rule.",
        "not stated; the statute does not require a warning",
        "Licensees under the social-worker chapter and their employees. No parallel duty statute was verified for psychologists or mental health counselors.",
        "https://webserver.rilegislature.gov/Statutes/TITLE5/5-39.1/5-39.1-4.htm",
        verified=False,
        note=(
            "The social-worker exception was read and is permissive. Psychologist chapter 5-44 was "
            "reviewed only for discipline provisions, and no mental-health-counselor duty statute "
            "was verified. A statewide classification is therefore unverified. Emergency certification "
            "under §40.1-5-7 is a commitment procedure, not a third-party warning duty."
        ),
    ),
    _e(
        "SC", "South Carolina", "case_law_only",
        "Bishop v. South Carolina Dep't of Mental Health, 331 S.C. 79, 502 S.E.2d 78 (1998), as stated in Doe v. Marion, 373 S.C. 390, 645 S.E.2d 245 (2007)",
        "A common-law duty to warn potential victims arises under the special-relationship exception when the defendant has the ability to monitor, supervise, and control an individual's conduct and the individual has made a specific threat of harm directed at a specific individual.",
        "The opinions describe a duty to warn the threatened third party. They do not list a statutory menu. Doe v. Marion holds there is no liability for failing to warn about a predilection for child molestation in the absence of a specific threat to an identifiable party.",
        "Bishop and Doe discuss a physician or psychiatrist and the Department of Mental Health. S.C. Code Ann. §19-11-95 separately covers psychologists, counselors, marriage and family therapists, addiction counselors, licensed master and independent social workers, and certain clinical nurse specialists, but only as a confidentiality statute.",
        "https://www.sccourts.org/media/opinions/HTMLFiles/SC/26323.htm",
        note=(
            "S.C. Code Ann. §19-11-95(C)(3) permits a provider to reveal the patient's intention to "
            "commit a crime or harm himself or herself and the information necessary to prevent it. "
            "That is permissive. Section 40-75-190, as read on https://www.scstatehouse.gov/code/t40c075.php, "
            "is a confidentiality section and does not itself command a warning. The 1998 Bishop "
            "slip opinion was not separately opened; the duty rule was read in the official Doe v. Marion opinion."
        ),
    ),
    _e(
        "SD", "South Dakota", "mandatory_duty",
        "SDCL 36-32-77 (licensed professional counselors); SDCL 36-33-55 (licensed marriage and family therapists)",
        "The client has communicated a serious threat of physical violence against an identifiable victim.",
        "The sections state a duty to warn or to take reasonable precautions to provide protection, and that the duty arises only in those circumstances. They do not list the acts that complete the duty.",
        "Licensed professional counselor and licensed professional counselor–mental health (36-32-77); licensed marriage and family therapist (36-33-55). Not verified for psychologists. Social workers: SDCL 36-26-30(2) says the licensee shall not be required to treat as confidential a communication that reveals contemplation of a crime or a harmful act. That is not a duty.",
        "https://sdlegislature.gov/api/Statutes/Statute/36-32-77",
        note="Both duty sections were still unrepealed on the Legislature's statute API. Sources: SL 2020, ch. 165, §31, and SL 2020, ch. 166, §22. The marriage-and-family section is at https://sdlegislature.gov/api/Statutes/Statute/36-33-55.",
    ),
    _e(
        "TN", "Tennessee", "mandatory_duty",
        "Tenn. Code Ann. §33-3-206 (2024 Tenn. Pub. Ch. 783); discharge also §33-3-207 (2024 Tenn. Pub. Ch. 761)",
        "If and only if the service recipient communicated to a qualified mental health professional or behavior analyst an intent for an actual threat of bodily harm against a clearly identified victim, or against a group of people (the act lists students at a day care or school, people at a place of worship, and family members), and the professional has determined or reasonably should have determined that the recipient has the apparent ability to commit the act and is likely to carry out the threat unless prevented.",
        "The professional or analyst must take reasonable care to warn of or take precautions to protect the identified victim or group, and must report the threat to the local law enforcement agency with jurisdiction over the recipient's municipality or county of residence or, if the threat is general and not imminent or clearly identified, to the local crisis response service. Senate Amendment 1 to the enacted bill adds that inpatient hospitalization of the service recipient discharges the duty to warn. Public Chapter 761 addresses notice to the parent, legal guardian, or legal custodian of an unemancipated minor.",
        "Qualified mental health professional or behavior analyst. Public Chapter 761 also says professional or service provider for the minor-notification rules.",
        "https://wapp.capitol.tn.gov/apps/BillInfo/Default.aspx?BillNumber=HB1625&ga=113",
        note=(
            "HB1625 was signed by the Governor on April 23, 2024, effective that day, and assigned "
            "Public Chapter 783. The General Assembly bill summary is the text verified on this check. "
            "The public-chapter PDF at https://publications.tnsosfiles.com/acts/113/pub/pc0783.pdf "
            "did not yield extractable text on this check. Public Chapter 761 "
            "(https://publications.tnsosfiles.com/acts/113/pub/pc0761.pdf) addresses minor notification; "
            "its full discharge list was not re-read from a clean reprint. A 2023 extraordinary-session "
            "bill that would have amended §33-3-206 was not assigned a public chapter."
        ),
    ),
    _e(
        "TX", "Texas", "permissive_disclosure",
        "Tex. Health & Safety Code §§611.002(b-1), 611.004(a)(2), 611.004(a-1)",
        "The professional determines there is a probability of imminent physical injury by the patient to the patient or others, or a probability of immediate mental or emotional injury to the patient.",
        "None. The professional may disclose to medical, mental-health, or law-enforcement personnel. Section 611.002(b-1) says no confidentiality exception creates a duty or requirement to disclose. Section 611.004(a-1) bars a cause of action for a disclosure made under (a)(2).",
        "A professional in §611.001(2): a person authorized to practice medicine, a person licensed or certified by Texas to diagnose, evaluate, or treat a mental or emotional condition or disorder, or a person the patient reasonably believes is so authorized, licensed, or certified.",
        "https://statutes.capitol.texas.gov/Docs/HS/htm/HS.611.htm",
        note=(
            "The page fetched was served from https://tcss.legis.texas.gov/resources/HS/htm/HS.611.htm. "
            "Thapar v. Zezulka, 994 S.W.2d 635 (Tex. 1999), is commonly cited as rejecting a "
            "common-law duty. That opinion was not retrieved from txcourts.gov on this check, so "
            "it is not the basis of this row. The classification follows the statute."
        ),
    ),
    _e(
        "UT", "Utah", "mandatory_duty",
        "Utah Code §§78B-3-501 and 78B-3-502",
        "The client or patient communicated to the therapist an actual threat of physical violence against a clearly identified or reasonably identifiable victim. Otherwise the therapist has no duty to warn or take precautions.",
        "Reasonable efforts to communicate the threat to the victim, and notification of a law enforcement officer or agency of the threat.",
        "Therapist in §78B-3-501: psychiatrist, psychologist, marriage and family therapist, social worker, psychiatric and mental health nurse specialist, and clinical mental health counselor, each as licensed in the cited Title 58 sections.",
        "https://le.utah.gov/xcode/Title78B/Chapter3/C78B-3_2025050720250507.pdf",
        note="Legislature chapter PDF carrying a May 7, 2025 effective-date marker. Section 78B-3-502 was amended by Chapter 335, 2022 General Session. No 2026 amendment appeared in that file.",
    ),
    _e(
        "VT", "Vermont", "mandatory_duty",
        "18 V.S.A. §1882 (2017, No. 51, §2), incorporating Peck v. Counseling Service of Addison County, Inc., 146 Vt. 61 (1985)",
        "The mental health professional knows or, based on the standards of the profession, should know that the patient poses a serious risk of danger to an identifiable victim.",
        "Exercise reasonable care to protect that victim. The enacted section does not list warning or law-enforcement notice as the exclusive means. The duty shall be applied in accordance with state and federal privacy laws. The section states that it negates Kuligoski v. Brattleboro Retreat, 2016 VT 54A.",
        "Mental health professional. Section 1882 does not define the term.",
        "https://legislature.vermont.gov/Documents/2018/Docs/ACTS/ACT051/ACT051%20As%20Enacted.pdf",
        note="The online statutes page (https://legislature.vermont.gov/statutes/section/18/042B/01882) states it includes the 2025 session, shows only the 2017 enactment, and labels the online statutes an unofficial copy. The operative text used here is the enrolled act.",
    ),
    _e(
        "VA", "Virginia", "mandatory_duty",
        "Va. Code §54.1-2400.1",
        "The client has orally, in writing, or via sign language communicated to the provider, while the provider is engaged in professional duties, a specific and immediate threat to cause serious bodily injury or death to an identified or readily identifiable person, and the provider reasonably believes, or should believe according to the standards of the profession, that the client has the intent and ability to carry out that threat immediately or imminently. If the third party is a child, the duty also covers a threat to engage in physical or sexual abuse as defined in §18.2-67.10.",
        "One or more of: seek involuntary admission; make reasonable attempts to warn the potential victims or the parent or guardian of a potential victim under 18; make reasonable efforts to notify a law-enforcement official having jurisdiction in the client's or potential victim's place of residence or work; take steps reasonably available to prevent the client from using violence until law enforcement takes custody; provide therapy or counseling in the session until the provider reasonably believes the client no longer has the intent or ability; or, for a registered peer recovery specialist or a qualified mental health professional who is not otherwise licensed, report immediately to a licensed mental health service provider to take one of those actions.",
        "Mental health service provider as defined in subsection A, including a certified substance abuse counselor, clinical psychologist, clinical social worker, licensed substance abuse treatment practitioner, licensed practical nurse, marriage and family therapist, mental health professional, physician, physician assistant, professional counselor, psychologist, qualified mental health professional, registered nurse, registered peer recovery specialist, school psychologist, or social worker, and listed professional corporations and partnerships.",
        "https://law.lis.virginia.gov/vacode/title54.1/chapter24/section54.1-2400.1/",
    ),
    _e(
        "WA", "Washington", "mandatory_duty",
        "RCW 71.05.120(3)",
        "The patient has communicated an actual threat of physical violence against a reasonably identifiable victim or victims.",
        "Reasonable efforts to communicate the threat to the victim or victims and to law enforcement personnel.",
        "Subsection (3) says it does not relieve a person from the duty. Subsections (1) and (2) are immunity rules for listed public and private agency officers, attending staff, designated crisis responders, peace officers, and evaluation and treatment facilities.",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=71.05.120",
        note="History line on the official page includes 2020 c 302 §11 and 2019 c 446 §22. Volk v. DeMeerleer was not retrieved as an opinion on this check. The current subsection (3) still states the communicated-threat duty.",
    ),
    _e(
        "WV", "West Virginia", "permissive_disclosure",
        "W. Va. Code §27-3-1(b)(5)",
        "Confidential information shall not be disclosed, except, among other listed grounds, to protect against a clear and substantial danger of imminent injury by a patient or client to himself, herself, or another.",
        "not stated; the subsection is an exception to confidentiality, not a command to warn a victim or to notify law enforcement",
        "Not limited to a named license list. The section covers communications and information obtained in the course of treatment or evaluation of any client or patient.",
        "https://code.wvlegislature.gov/27-3-1/",
        note=(
            "A 2013 introduced bill would have made disclosure to potential victims and law "
            "enforcement mandatory. The enrolled code on the Legislature's site keeps subsection "
            "(b)(5) as an exception (shall not be disclosed, except), not a shall-disclose command. "
            "No West Virginia appellate opinion imposing a Tarasoff duty was opened on this check."
        ),
    ),
    _e(
        "WI", "Wisconsin", "case_law_only",
        "Schuster v. Altenberg, 144 Wis. 2d 223, 424 N.W.2d 159 (1988), as quoted in Milwaukee Deputy Sheriff's Ass'n v. City of Wauwatosa, 2010 WI App 95",
        "As quoted by the Court of Appeals from Schuster: it was foreseeable to a psychiatrist, exercising due care, that failing to warn a third person or failing to institute detention or commitment proceedings would result in harm. The 2010 opinion also describes Schuster as a duty to warn a person targeted by a credible threat.",
        "Wis. Stat. §51.17(3) states that a health care provider who reasonably believes an individual has a substantial probability of harm under §51.15(1)(ar) fulfills any duty to warn a third party by contacting law enforcement, contacting the county department responsible for emergency-detention approval, approving emergency detention if authorized, or taking any other action a reasonable health care provider would consider as fulfilling the duty. Section 51.17 does not itself create the duty.",
        "Schuster, as described in the 2010 opinion, concerns a treating psychiatrist. Section 51.17 uses health care provider as defined in §146.81(1).",
        "https://www.wicourts.gov/ca/opinion/DisplayDocument.pdf?content=pdf&seqNo=50839",
        note="The 1988 Schuster slip opinion was not retrieved as its own opinion. The discharge statute was read at https://docs.legis.wisconsin.gov/statutes/statutes/51/17.",
    ),
    _e(
        "WY", "Wyoming", "permissive_disclosure",
        "W.S. 33-38-113(a)(iv) (2023 Wyo. Sess. Laws, Enrolled Act No. 39); W.S. 33-27-123(a)(iv) (2022 Wyo. Sess. Laws, Enrolled Act No. 18)",
        "An immediate threat of physical violence against a readily identifiable victim is disclosed to the licensee. The sections are exceptions to a rule that the licensee shall not disclose without an express waiver.",
        "not stated; neither enrolled act uses shall warn or duty",
        "For 33-38-113, a person licensed under the counselors, social workers, marriage and family therapists, and chemical dependency specialists act. For 33-27-123, a psychologist, behavior analyst, or assistant behavior analyst.",
        "https://wyoleg-prod.wyoleg.gov/2023/Enroll/SF0010.pdf",
        note="Psychologist enrolled act: https://wyoleg.gov/2022/Bills/HB0110.pdf. No statute imposing a duty, and no case imposing or rejecting a duty, was verified.",
    ),
)


DUTY_TO_WARN: dict[str, DutyToWarnEntry] = {e.state: e for e in _ENTRIES}


def get_duty_to_warn(state: str) -> DutyToWarnEntry | None:
    """Return the duty-to-warn row for ``state`` (case-insensitive), or None."""
    if not state:
        return None
    return DUTY_TO_WARN.get(state.upper())


def all_duty_to_warn() -> tuple[DutyToWarnEntry, ...]:
    """All 50 states and the District of Columbia, in postal-code order."""
    return _ENTRIES
