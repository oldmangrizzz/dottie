"""Read-only cross-multidimensional evidence bridge for the Dottie research harness.

The bridge accepts an explicit principal and a trusted scope resolver. It never
turns traversal paths into assertions or grants permissions via caller-provided
scope names. No external action or autobiographical promotion is implemented.
"""
from dataclasses import dataclass


DIMENSIONS = frozenset(("temporal", "causal", "semantic", "contextual", "evidentiary", "agent"))


@dataclass(frozen=True)
class Connection:
    source: str
    target: str
    dimension: str
    evidence_ref: str
    status: str = "association"

    def __post_init__(self):
        if self.dimension not in DIMENSIONS:
            raise ValueError("Unknown dimension")
        if self.status not in ("association", "verified"):
            raise ValueError("Unknown evidence status")
        if not all(isinstance(v, str) and v.strip() for v in
                   (self.source, self.target, self.evidence_ref)):
            raise ValueError("Connection endpoints and evidence reference required")


class CrossDimensionalBridge:
    def __init__(self, authorize):
        if not callable(authorize):
            raise TypeError("A trusted authorization callback is required")
        self._authorize = authorize
        self._connections = []

    def connect(self, principal, scope, connection):
        if not self._authorize(principal, scope, "write"):
            raise PermissionError("Write denied")
        if not isinstance(connection, Connection):
            raise TypeError("Expected Connection")
        self._connections.append((scope, connection))

    def traverse(self, principal, scope, seed, max_hops=3):
        if not self._authorize(principal, scope, "read"):
            raise PermissionError("Read denied")
        if type(max_hops) is not int or not 1 <= max_hops <= 10:
            raise ValueError("max_hops must be between 1 and 10")
        paths = []
        frontier = [(seed, (), frozenset((seed,)))]
        for _ in range(max_hops):
            following = []
            for node, path, visited in frontier:
                for edge_scope, edge in self._connections:
                    if edge_scope != scope or edge.source != node or edge.target in visited:
                        continue
                    new_path = path + (edge,)
                    paths.append(new_path)
                    following.append((edge.target, new_path, visited | {edge.target}))
            frontier = following
        return tuple(paths)
