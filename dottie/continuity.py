"""Local continuity boundary for persistent identity and experience.

Does not implement inference, cognitive agency, or a production approval authority.
"""
from pathlib import Path
from .identity_store import IdentityStore
from .experience_store import ExperienceStore


class DottieContinuity:
    def __init__(self, root, approval_validator=None):
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        self.identities = IdentityStore(root / "identities.sqlite")
        self.experiences = ExperienceStore(
            root / "experiences.sqlite", approval_validator=approval_validator
        )

    def establish(self, identity_id, baseline_ref):
        self.identities.establish(identity_id, baseline_ref)

    def identity(self, identity_id):
        return self.identities.read(identity_id)

    def observe(self, identity_id, mission, kind, content, source_ref):
        self.identities.read(identity_id)
        return self.experiences.record(identity_id, mission, kind, content, source_ref)

    def consolidate(self, identity_id, event_id, review_receipt):
        self.identities.read(identity_id)
        return self.experiences.promote(identity_id, event_id, review_receipt)

    def close(self):
        self.experiences.close()
        self.identities.close()
