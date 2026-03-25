"""Core DataNarrate engine — narrators and storyteller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd

from datanarrate.config import NarrativeConfig, Tone
from datanarrate.utils import (
    compute_trend_direction,
    detect_outliers,
    first_string_column,
    fmt_number,
    fmt_pct,
    numeric_columns,
    pct_change,
    safe_mean,
)


# ---------------------------------------------------------------------------
# Trend narrator
# ---------------------------------------------------------------------------

class TrendNarrator:
    """Describe trends in sequential numeric data."""

    def __init__(self, config: NarrativeConfig | None = None) -> None:
        self.config = config or NarrativeConfig()

    def narrate(
        self,
        df: pd.DataFrame,
        metric: str,
        period_col: str | None = None,
    ) -> List[str]:
        """Generate trend narratives for *metric* over ordered rows."""
        if metric not in df.columns:
            return []
        values = df[metric].dropna().tolist()
        if len(values) < 2:
            return []

        periods = df[period_col].tolist() if period_col and period_col in df.columns else list(range(len(values)))
        direction = compute_trend_direction(values, self.config.trend_stability_pct)
        change = pct_change(values[0], values[-1])
        abs_change = fmt_pct(abs(change))

        tpl_key = f"trend_{direction}"
        tpl = self.config.get_template(tpl_key)
        if not tpl:
            return []

        narrative = tpl.format(
            metric=metric,
            change=abs_change,
            start_period=str(periods[0]),
            end_period=str(periods[-1]),
            start_value=fmt_number(values[0]),
            end_value=fmt_number(values[-1]),
        )
        return [narrative]


# ---------------------------------------------------------------------------
# Comparison narrator
# ---------------------------------------------------------------------------

class ComparisonNarrator:
    """Compare aggregated metric values across groups."""

    def __init__(self, config: NarrativeConfig | None = None) -> None:
        self.config = config or NarrativeConfig()

    def narrate(
        self,
        df: pd.DataFrame,
        metric: str,
        group_col: str,
    ) -> List[str]:
        """Compare the top two groups by mean *metric*."""
        if metric not in df.columns or group_col not in df.columns:
            return []

        grouped = df.groupby(group_col)[metric].mean().sort_values(ascending=False)
        if len(grouped) < 2:
            return []

        narratives: List[str] = []
        top_groups = grouped.head(2)
        group_a, group_b = top_groups.index[0], top_groups.index[1]
        val_a, val_b = top_groups.iloc[0], top_groups.iloc[1]
        diff = pct_change(val_b, val_a)

        if abs(diff) < self.config.trend_stability_pct:
            tpl_key = "comparison_equal"
        elif diff > 0:
            tpl_key = "comparison_higher"
        else:
            tpl_key = "comparison_lower"

        tpl = self.config.get_template(tpl_key)
        if tpl:
            narrative = tpl.format(
                group_a=group_a,
                group_b=group_b,
                difference=fmt_pct(abs(diff)),
                metric=metric,
                value_a=fmt_number(val_a),
                value_b=fmt_number(val_b),
            )
            narratives.append(narrative)
        return narratives


# ---------------------------------------------------------------------------
# Outlier narrator
# ---------------------------------------------------------------------------

class OutlierNarrator:
    """Highlight anomalous values in a metric."""

    def __init__(self, config: NarrativeConfig | None = None) -> None:
        self.config = config or NarrativeConfig()

    def narrate(
        self,
        df: pd.DataFrame,
        metric: str,
        period_col: str | None = None,
    ) -> List[str]:
        """Detect outliers in *metric* and describe them."""
        if metric not in df.columns:
            return []

        outliers = detect_outliers(df[metric], self.config.outlier_threshold)
        if outliers.empty:
            return []

        mean_val = df[metric].mean()
        narratives: List[str] = []

        for _, row in outliers.iterrows():
            idx = row["index"]
            value = row["value"]
            factor = round(value / mean_val, 1) if mean_val != 0 else 0

            period = str(df.at[idx, period_col]) if period_col and period_col in df.columns else f"Row {idx}"
            tpl_key = "outlier_high" if row["z_score"] > 0 else "outlier_low"
            tpl = self.config.get_template(tpl_key)
            if tpl:
                narratives.append(
                    tpl.format(
                        period=period,
                        value=fmt_number(value),
                        metric=metric,
                        factor=abs(factor),
                        average=fmt_number(mean_val),
                    )
                )
        return narratives


# ---------------------------------------------------------------------------
# Summary narrator
# ---------------------------------------------------------------------------

class SummaryNarrator:
    """Produce an executive summary of a DataFrame."""

    def __init__(self, config: NarrativeConfig | None = None) -> None:
        self.config = config or NarrativeConfig()

    def narrate(self, df: pd.DataFrame) -> List[str]:
        """Generate summary narratives covering shape and key stats."""
        narratives: List[str] = []

        header_tpl = self.config.get_template("summary_header")
        if header_tpl:
            narratives.append(
                header_tpl.format(
                    record_count=len(df),
                    column_count=len(df.columns),
                )
            )

        num_cols = numeric_columns(df)
        metric_tpl = self.config.get_template("summary_top_metric")
        for col in num_cols:
            if metric_tpl:
                narratives.append(
                    metric_tpl.format(
                        metric=col,
                        max_value=fmt_number(df[col].max()),
                        min_value=fmt_number(df[col].min()),
                        mean_value=fmt_number(df[col].mean()),
                    )
                )
        return narratives


# ---------------------------------------------------------------------------
# Main storyteller
# ---------------------------------------------------------------------------

class DataStoryteller:
    """Orchestrate all narrators to produce a full data story."""

    def __init__(self, config: NarrativeConfig | None = None) -> None:
        self.config = config or NarrativeConfig()
        self.trend = TrendNarrator(self.config)
        self.comparison = ComparisonNarrator(self.config)
        self.outlier = OutlierNarrator(self.config)
        self.summary = SummaryNarrator(self.config)

    # -- data loading -------------------------------------------------------

    @staticmethod
    def load(path: str | Path) -> pd.DataFrame:
        """Load a CSV or JSON file into a DataFrame."""
        path = Path(path)
        if path.suffix.lower() == ".json":
            return pd.read_json(path)
        return pd.read_csv(path)

    # -- full narrative generation ------------------------------------------

    def tell_story(
        self,
        df: pd.DataFrame,
        period_col: str | None = None,
        group_col: str | None = None,
    ) -> List[str]:
        """Generate a complete narrative for *df*.

        Parameters
        ----------
        df : pd.DataFrame
            The dataset to narrate.
        period_col : str | None
            Column representing time periods (for trends / outliers).
        group_col : str | None
            Column representing categorical groups (for comparisons).

        Returns
        -------
        list[str]
            Ordered narrative sentences.
        """
        if period_col is None:
            period_col = first_string_column(df)
        if group_col is None:
            group_col = first_string_column(df)

        narratives: List[str] = []

        # 1. Summary
        narratives.extend(self.summary.narrate(df))

        # 2. Trends & outliers for each numeric column
        num_cols = numeric_columns(df)
        for col in num_cols:
            narratives.extend(self.trend.narrate(df, col, period_col))
            narratives.extend(self.outlier.narrate(df, col, period_col))

        # 3. Comparisons (if a group column exists)
        if group_col and group_col in df.columns:
            for col in num_cols:
                narratives.extend(self.comparison.narrate(df, col, group_col))

        return narratives[: self.config.max_narratives]

    def generate_report(
        self,
        df: pd.DataFrame,
        title: str = "Data Narrative Report",
        period_col: str | None = None,
        group_col: str | None = None,
    ) -> str:
        """Return a Markdown-formatted report."""
        sentences = self.tell_story(df, period_col, group_col)
        lines = [f"# {title}", ""]
        for sentence in sentences:
            lines.append(f"- {sentence}")
        lines.append("")
        lines.append(
            f"*Report generated by DataNarrate v0.1.0 | Tone: {self.config.tone.value}*"
        )
        return "\n".join(lines)
