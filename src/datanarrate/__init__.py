"""DataNarrate — turn datasets into natural language narratives."""

__version__ = "0.1.0"

from datanarrate.core import (
    ComparisonNarrator,
    DataStoryteller,
    OutlierNarrator,
    SummaryNarrator,
    TrendNarrator,
)
from datanarrate.config import NarrativeConfig, Tone

__all__ = [
    "DataStoryteller",
    "TrendNarrator",
    "ComparisonNarrator",
    "OutlierNarrator",
    "SummaryNarrator",
    "NarrativeConfig",
    "Tone",
]
