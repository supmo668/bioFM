"""Framework-free reference implementations of test-time compute strategies.

Each module implements one canonical TTC method in <= 80 lines, using only the
Python stdlib. See ``GUIDE.md`` for the taxonomy these map onto.
"""

from ref_impl.adaptive_budget import adaptive_route
from ref_impl.best_of_n import best_of_n
from ref_impl.iterative_revision import iterative_revision
from ref_impl.majority_vote import majority_vote
from ref_impl.types import Candidate, Generator, Verifier
from ref_impl.weighted_majority import weighted_majority

__all__ = [
    "Candidate",
    "Generator",
    "Verifier",
    "adaptive_route",
    "best_of_n",
    "iterative_revision",
    "majority_vote",
    "weighted_majority",
]
