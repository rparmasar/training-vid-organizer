"""Data models for training video organizer."""

from dataclasses import dataclass, field


@dataclass
class LiftEntry:
    """Represents a single lift entry in the database."""

    date: str
    bodyweight: float | None = None
    lift: str = ""
    weight: float = 0.0
    reps: int = 0
    top_set: bool = False
    reps_in_reserve: int | None = None
    filepath: str | None = None
    program: str | None = None
    program_iteration: int | None = None
