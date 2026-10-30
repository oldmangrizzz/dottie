"""Minimal explicit authority boundary for Dottie actions."""


def authorize(action: str, grants: set[str]) -> bool:
    """Allow only exact, non-wildcard grants; deny everything else."""
    return bool(action) and action != '*' and action in grants
