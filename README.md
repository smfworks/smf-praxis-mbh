# smf-praxis-mbh

**SMF Praxis Mental/Behavioral Health vertical pack** — the
Mental/Behavioral Health (MBH) build for the [Praxis](https://github.com/smfworks/smf-praxis)
governed agent platform.

**Not legal or clinical advice.** The jurisdiction tables in this pack are
decision-support ground. Verify them with your state board and counsel before
you rely on them. Praxis does not diagnose, determine treatment, or establish
a therapeutic relationship.

This vertical equips Praxis for licensed mental/behavioral health professionals
(psychiatrists, psychologists, licensed clinical social workers, licensed
counselors, MFTs) and their practice staff across 13 US states: FL, GA, SC, TN,
VA, WV, MD, PA, OH, NJ, NY, CT, MA.

## What it ships

- **`behavioral_health` pack** — persona, knowledge base, tool allowlist,
  HIPAA-aware risk policy (READ + DRAFT autonomous; SEND + DESTRUCTIVE held
  for clinician dual approval), and 8 domain skills.
- **8 compliance modules** shipped in this package:
  - `psychotherapy_notes_governance` — 45 CFR §164.508 specific-authorization;
    Praxis drafts progress notes only, never psychotherapy notes.
  - `crisis_safety_gate` — duty-to-warn/protect (Tarasoff) assessment +
    safety-plan scaffolding; protective action is SEND-held.
  - `mandated_reporting` — child/dependent-adult/elder abuse report scaffold
    with per-state SCR windows; clinician is reporter of record.
  - `minor_consent_mh` — per-state minor-consent-for-MH age floor applied to
    record access and portal communications.
  - `treatment_planning_attestation` — treatment-plan drafts route for
    clinician attestation before entering the clinical record.
  - `part2_governance` — 42 CFR Part 2 SUD-record governance: specific
    written consent, re-disclosure prohibition, court-order for law
    enforcement.
  - `mh_jurisdictions` — 13-state + CA (Tarasoff-canonical) MH regulatory
    profiles.
  - `records_retention_mh` — MH-record retention with psychotherapy-note
    patient-access carve-out and Part 2 re-disclosure persistence.
- **6 manual eval cases** + 2 generic (persona + posture) = 8 vertical eval
  cases covering: never-write-psychotherapy-note, duty-to-warn,
  mandated-reporter, minor-consent-MH, treatment-plan attestation,
  42 CFR Part 2 re-disclosure block.

## Compliance posture

- **Compliance mode:** `enforced`
- **Autonomous:** `READ`, `DRAFT`
- **Held for clinician approval:** `SEND`, `DESTRUCTIVE`
- **Non-negotiable guardrails** (in the persona + enforced by modules):
  never write to the clinical record autonomously; never draft psychotherapy
  notes; never diagnose / determine treatment / establish a therapeutic
  relationship; never contact a victim, law enforcement, or a hospital
  autonomously; never file a mandated report as the reporter of record.

## Installation

This vertical depends on the open-core Praxis base. Both are MIT-licensed.

```bash
pip install praxis-agent        # open-core base (MIT)
pip install praxis-mbh          # this vertical (MIT)
```

Activating the vertical lights up the `behavioral_health` pack, its dashboard
routes, and the `vertical.behavioral_health.*` eval cases for the whole
process lifetime (registration is import-time and process-global).

## Verification

From a checkout of the base with this vertical installed editable:

```bash
pytest tests/ -q                          # this vertical's test suite
python -m hybridagent.cli eval            # base evals (30/30) stay green
python -m hybridagent.cli demo            # base demo stays green
ruff check hybridagent_praxis_mbh/        # lint clean
```

## License

MIT. Copyright (c) 2026 SMF Works. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

As of 2026, SMF Works relicenses all prior versions and tags of this project
(including v0.1.x and v0.2.x) under the MIT License.

Not legal or clinical advice. Verify duty-to-warn and other jurisdiction
facts with your state board and counsel.