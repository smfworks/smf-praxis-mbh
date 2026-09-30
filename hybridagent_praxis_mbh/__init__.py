"""SMF Praxis Mental/Behavioral Health vertical — registration module.

This package is the Mental/Behavioral Health (MBH) vertical build for Praxis,
licensed under the MIT License. It depends on the open-core ``praxis-agent``
base and registers the MBH vertical's spec and eval cases with the base's
:mod:`hybridagent.verticals.registry` on import.

Installation::

    pip install praxis-agent      # open-core base (MIT)
    pip install praxis-mbh        # this vertical (MIT)

Activating the vertical lights up:

  * the ``behavioral_health`` vertical pack (persona + knowledge + HIPAA +
    42 CFR Part 2 SUD-record governance + psychotherapy-note protections +
    crisis-safety gate + duty-to-warn/Tarasoff + mandated-reporter workflow +
    minor-consent-for-MH + treatment-planning attestation + records-retention),
  * the ``vertical.behavioral_health.*`` eval cases (never-write-psychotherapy-
    note, duty-to-warn gate, mandated-reporter workflow, minor MH consent,
    treatment-plan attestation, 42 CFR Part 2 re-disclosure block).

The vertical-specific modules are imported lazily by the eval cases and
daemon routes that need them.

Compliance mode: ``enforced``. READ + DRAFT autonomous; SEND + DESTRUCTIVE
held for human (clinician) approval. The behavioral-health persona carries
"never write to the clinical record / psychotherapy notes autonomously" +
"do not diagnose, do not determine treatment, do not establish a therapeutic
relationship" guardrails across all 13 states, with HIPAA as the federal
floor and 42 CFR Part 2 as the heightened SUD-record floor.
"""

from __future__ import annotations

from .registration import register

__version__ = "0.2.1"

__all__ = ["__version__", "register"]

# Auto-register on import so ``import hybridagent_praxis_mbh`` lights up
# the vertical for the whole process lifetime.
register()