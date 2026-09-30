"""Training Video Organizer - A CLI tool for managing training videos."""

__version__ = "0.1.0"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .commands.categorize import Categorizer
    from .commands.metadata import MetadataExtractor
    from .commands.search import VideoSearcher

__all__ = [
    "__version__",
    "Categorizer",
    "MetadataExtractor",
    "VideoSearcher",
]
