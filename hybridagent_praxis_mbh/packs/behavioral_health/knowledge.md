# Mental/Behavioral Health Pack — Knowledge Base

This knowledge base is ingested into the `pack:behavioral_health` RAG namespace on pack activation. It grounds Praxis's clinical-documentation and compliance outputs across the 13 states the pack covers: FL, GA, SC, TN, VA, WV, MD, PA, OH, NJ, NY, CT, MA.

## 1. The 13-state mental/behavioral health quick reference

| State | Board | Duty to warn | SCR window (child) | Minor MH consent age | Retention (adult/minor) | Data-security |
|---|---|---|---|---|---|---|
| FL | FL Board of CSW/MFT/MHC | no statutory duty | 24h | 13 | 5yr / 7yr | breach-notification |
| GA | GA Composite Board (Counselors/SW/MFT) | duty to protect | 24h | 13 | 5yr / 7yr | breach-notification |
| SC | SC Board of SW Examiners (LLR) | no statutory duty | 24h | 14 | 5yr / 7yr | breach-notification |
| TN | TN Health Related Boards (SW) | no statutory duty | 24h | 13 | 7yr / 7yr | breach-notification |
| VA | VA Board of Counseling (DHP) | no statutory duty | 24h | 14 | 6yr / 3yr | breach-notification |
| WV | WV Board of SW Examiners | no statutory duty | 24h | 14 | 5yr / 7yr | breach-notification |
| MD | MD Board of SW / Professional Counselors | no statutory duty | 24h | 14 | 5yr / 7yr | breach-notification |
| PA | PA State Board of SW/MFT/PC | no statutory duty | 24h | 14 | 7yr / 21 | breach-notification |
| OH | OH Counselor/SW/MFT Board | no statutory duty | 24h | 14 | 5yr / 7yr | breach-notification |
| NJ | NJ Board of SW Examiners / MFT | no statutory duty | 24h | 14 | 6yr / 21 | breach-notification |
| NY | NYSED Office of the Professions (SW/MHP) | duty to protect | 24h | 14 | 6yr / 21+ | **SHIELD obligation** |
| CT | CT DPH (SW/Counseling/MFT) | duty to protect | 24h | 14 | 6yr / 21 | breach-notification |
| MA | MA Board of SW / Allied MH | duty to protect | 24h | 14 | 7yr / 21+ | **WISP mandate (201 CMR 17.00)** |

Note: CA (outside the 13-state registry) is the canonical Tarasoff-codified jurisdiction; the gate module carries a CA profile for the duty-to-warn eval. The 13 registry states mostly impose a duty to *protect* (NY/CT/MA) or leave it to clinician judgment under ethics rules.

## 2. Governance line (non-negotiable)

- **Never write to the clinical record autonomously.** Treatment-plan and progress-note drafts route for clinician attestation (`treatment_planning_attestation` / `psychotherapy_notes_governance`).
- **Never draft psychotherapy notes.** Psychotherapy notes are the clinician's private process notes; Praxis may draft progress notes only (45 CFR §164.508).
- **Never diagnose, determine treatment, or establish a therapeutic relationship.** Praxis is a documentation and compliance assistant, not a clinician.
- **Never contact a victim, law enforcement, or a hospital autonomously.** Duty-to-warn/protect protective action is SEND-held for clinician approval; the clinician — not Praxis — decides whether the duty applies.
- **Never file a mandated report as the reporter of record.** Praxis drafts the scaffold; the clinician files with the SCR (SEND-held).
- **PHI = minimum necessary.** HIPAA purpose-of-use + accounting-of-disclosures + breach workflow (reuses the medical vertical's HIPAA governance).
- **42 CFR Part 2 for SUD records.** Specific written consent for most disclosures; general HIPAA TPO consent does NOT cover Part 2 records; re-disclosure prohibition notice must accompany every permitted Part 2 disclosure; law enforcement / bare subpoena need a qualifying court order.
- **Minor consent for MH:** apply the state's age floor to record access; parent access to self-consented confidential MH encounters requires the minor's authorization.

## 3. Duty to warn / protect (Tarasoff-line)

1. **Credible serious threat of physical violence against a reasonably identifiable victim** triggers a duty analysis.
2. State standard: codified (CA), common-law, duty-to-protect (NY/CT/MA), or no statutory duty (clinician judgment under ethics rules).
3. Praxis surfaces the standard + citation and routes protective action (warn victim / notify law enforcement / hospitalize) to the clinician — SEND-held.
4. Known history of violence + stated intent to act elevate the finding to critical.
5. Suicidal crisis (separate) triggers a safety-plan scaffold, not a duty-to-warn report; civil-commitment standard surfaced from the state profile.

## 4. Mandated reporting

- All licensed MH professionals are mandated reporters in all 13 states.
- Child abuse: file with the state SCR within 24h (36h CA) of disclosure.
- Praxis drafts the report scaffold; the clinician is the reporter of record; filing is SEND-held.
- Dependent-adult and elder abuse follow the same workflow with the appropriate recipient (APS).

## 5. 42 CFR Part 2 (SUD records)

- Applies to federally assisted SUD treatment programs in every state.
- Specific written consent required for most disclosures (recipient, purpose, amount, expiration).
- General HIPAA TPO consent does NOT authorize Part 2 disclosures.
- Re-disclosure prohibition: the recipient may not re-disclose without new specific authorization; the notice MUST accompany every permitted disclosure.
- Law enforcement / bare subpoena: require a qualifying Part 2 court order (§2.65), not just consent.

## 6. Psychotherapy notes (45 CFR §164.508)

- Psychotherapy notes = the clinician's private, process-oriented notes documenting the content of a counseling session, kept separate from the rest of the record.
- Specific authorization required for any use or disclosure beyond the clinician's own treatment use.
- Praxis NEVER drafts psychotherapy notes — only progress notes.
- Patient-access carve-out: 45 CFR §164.528 limits the patient's right to inspect psychotherapy notes (specific authorization required to disclose).
- A payer cannot demand psychotherapy notes without specific authorization.

## 7. Minor consent for MH

- State age floors: FL=13, GA=13, SC=14, TN=13, VA=14, WV=14, MD=14, PA=14, OH=14, NJ=14, NY=14, CT=14, MA=14 (outpatient MH; some cap sessions or require parent notification after N sessions).
- Self-consented confidential MH encounters: parent portal/record-release access denied without the minor's authorization.
- Minor self-access and provider treatment access remain allowed.
- Psychotherapy notes need their own specific authorization regardless of the minor-consent gate.

## 8. Records retention + patient access

- Adult retention: 5–7 years from last visit (state-specific).
- Minor: often until age 21 or N years after last visit, whichever longer.
- Patient access deadlines: NY/MA = 10 days; FL/VA = 15; NJ = 7; MD = 21; others HIPAA 30-day floor.
- Psychotherapy notes carry the patient-access carve-out (45 CFR §164.528).
- Part 2 SUD records carry the re-disclosure prohibition indefinitely — retention does not extinguish Part 2 protections.
- Legal hold blocks disposal. Praxis never deletes autonomously (DESTRUCTIVE, dual approval).

## 9. Civil commitment (decision-support only)

- Praxis surfaces the state's civil-commitment standard (danger to self/others, gravely disabled, inability to care for self) when a patient is in acute crisis.
- Praxis never initiates an involuntary hold autonomously — clinician + facility action, SEND-held.
- Standards: FL Baker Act, GA, SC, TN, VA, WV, MD, PA (clear and present danger), OH, NJ, NY (likelihood of serious harm), CT, MA (likelihood of serious harm), CA LPS §5150.