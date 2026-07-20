from hybridagent.authority import AuthorityPolicy


def policy(jurisdiction: str) -> AuthorityPolicy:
    """Authority policy for the behavioral-health vertical.

    Behavioral-health practice guidance is grounded in clinical guidelines,
    systematic reviews, and peer-reviewed studies. Authority tiers decay on a
    2-year horizon (consistent with the medical vertical's clinical-evidence
    floor); statutory and board-rule citations are handled by the
    ``mh_jurisdictions`` profiles, not by this evidence-tier policy.
    """
    return AuthorityPolicy(
        "behavioral_health",
        jurisdiction,
        ("guideline", "systematic_review", "study"),
        730,
    )