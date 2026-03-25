"""Narrative templates and tone configuration."""

from __future__ import annotations

from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class Tone(str, Enum):
    """Supported narrative tones."""

    FORMAL = "formal"
    CASUAL = "casual"
    EXECUTIVE = "executive"


# ---------------------------------------------------------------------------
# Template bank – keyed by (narrator_type, tone)
# ---------------------------------------------------------------------------

TEMPLATES: Dict[str, Dict[Tone, str]] = {
    # Trend templates
    "trend_increase": {
        Tone.FORMAL: "{metric} increased by {change} from {start_period} to {end_period}, rising from {start_value} to {end_value}.",
        Tone.CASUAL: "{metric} went up {change} between {start_period} and {end_period} ({start_value} → {end_value}).",
        Tone.EXECUTIVE: "{metric} grew {change} ({start_period}–{end_period}), signaling positive momentum.",
    },
    "trend_decrease": {
        Tone.FORMAL: "{metric} decreased by {change} from {start_period} to {end_period}, falling from {start_value} to {end_value}.",
        Tone.CASUAL: "{metric} dropped {change} between {start_period} and {end_period} ({start_value} → {end_value}).",
        Tone.EXECUTIVE: "{metric} declined {change} ({start_period}–{end_period}), warranting attention.",
    },
    "trend_stable": {
        Tone.FORMAL: "{metric} remained relatively stable from {start_period} to {end_period}, holding near {start_value}.",
        Tone.CASUAL: "{metric} stayed pretty flat between {start_period} and {end_period} (around {start_value}).",
        Tone.EXECUTIVE: "{metric} held steady ({start_period}–{end_period}), indicating consistent performance.",
    },
    # Comparison templates
    "comparison_higher": {
        Tone.FORMAL: "{group_a} outperformed {group_b} by {difference} in {metric} ({value_a} vs {value_b}).",
        Tone.CASUAL: "{group_a} beat {group_b} by {difference} on {metric} ({value_a} vs {value_b}).",
        Tone.EXECUTIVE: "{group_a} leads {group_b} by {difference} in {metric}, a notable competitive gap.",
    },
    "comparison_lower": {
        Tone.FORMAL: "{group_a} underperformed {group_b} by {difference} in {metric} ({value_a} vs {value_b}).",
        Tone.CASUAL: "{group_a} lagged behind {group_b} by {difference} on {metric} ({value_a} vs {value_b}).",
        Tone.EXECUTIVE: "{group_a} trails {group_b} by {difference} in {metric}, requiring review.",
    },
    "comparison_equal": {
        Tone.FORMAL: "{group_a} and {group_b} performed similarly in {metric} (approximately {value_a}).",
        Tone.CASUAL: "{group_a} and {group_b} were neck and neck on {metric} (about {value_a}).",
        Tone.EXECUTIVE: "{group_a} and {group_b} are on par in {metric}, both near {value_a}.",
    },
    # Outlier templates
    "outlier_high": {
        Tone.FORMAL: "{period} recorded an unusually high value of {value} for {metric}, which is {factor}x the average of {average}.",
        Tone.CASUAL: "{period} saw a huge spike in {metric} — {value} vs the usual {average} ({factor}x!).",
        Tone.EXECUTIVE: "{period} exhibited an anomalous spike in {metric} at {value} ({factor}x average), meriting investigation.",
    },
    "outlier_low": {
        Tone.FORMAL: "{period} recorded an unusually low value of {value} for {metric}, which is {factor}x below the average of {average}.",
        Tone.CASUAL: "{period} had a big dip in {metric} — down to {value} vs the usual {average}.",
        Tone.EXECUTIVE: "{period} showed an unexpected dip in {metric} to {value} (avg {average}), flagged for review.",
    },
    # Summary templates
    "summary_header": {
        Tone.FORMAL: "Executive Summary: Analysis of {record_count} records across {column_count} dimensions.",
        Tone.CASUAL: "Here's the quick rundown from {record_count} data points across {column_count} fields.",
        Tone.EXECUTIVE: "Key Insights — {record_count} records, {column_count} dimensions analyzed.",
    },
    "summary_top_metric": {
        Tone.FORMAL: "The highest observed value for {metric} was {max_value}, while the lowest was {min_value} (mean: {mean_value}).",
        Tone.CASUAL: "{metric} ranged from {min_value} to {max_value}, averaging {mean_value}.",
        Tone.EXECUTIVE: "{metric}: range {min_value}–{max_value}, mean {mean_value}.",
    },
}


class NarrativeConfig(BaseModel):
    """Runtime configuration for narrative generation."""

    tone: Tone = Field(default=Tone.FORMAL, description="Narrative tone")
    outlier_threshold: float = Field(
        default=2.0,
        description="Standard deviations from mean to flag as outlier",
    )
    trend_stability_pct: float = Field(
        default=5.0,
        description="Percentage change below which a trend is considered stable",
    )
    max_narratives: int = Field(
        default=20,
        description="Maximum narrative sentences to generate",
    )

    def get_template(self, key: str) -> str:
        """Return the template string for the current tone."""
        templates = TEMPLATES.get(key, {})
        return templates.get(self.tone, templates.get(Tone.FORMAL, ""))
