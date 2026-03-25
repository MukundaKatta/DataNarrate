"""Statistical helpers, number formatting, and percentage calculations."""

from __future__ import annotations

from typing import Optional, Sequence, Union

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------

def fmt_number(value: float, decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
    """Format a number with optional prefix/suffix and thousands separators."""
    if abs(value) >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:,.{decimals}f}B"
    elif abs(value) >= 1_000_000:
        formatted = f"{value / 1_000_000:,.{decimals}f}M"
    elif abs(value) >= 1_000:
        formatted = f"{value / 1_000:,.{decimals}f}K"
    else:
        formatted = f"{value:,.{decimals}f}"
    return f"{prefix}{formatted}{suffix}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a value as a percentage string."""
    return f"{value:,.{decimals}f}%"


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def pct_change(old: float, new: float) -> float:
    """Compute percentage change from *old* to *new*."""
    if old == 0:
        return 0.0 if new == 0 else float("inf")
    return ((new - old) / abs(old)) * 100.0


def detect_outliers(
    series: pd.Series,
    threshold: float = 2.0,
) -> pd.DataFrame:
    """Return a DataFrame of outlier rows with columns [index, value, z_score].

    An outlier is any point whose absolute z-score exceeds *threshold*.
    """
    clean = series.dropna()
    if len(clean) < 3:
        return pd.DataFrame(columns=["index", "value", "z_score"])

    mean = clean.mean()
    std = clean.std(ddof=1)
    if std == 0:
        return pd.DataFrame(columns=["index", "value", "z_score"])

    z_scores = (clean - mean) / std
    mask = z_scores.abs() > threshold
    outlier_idx = clean[mask].index
    rows = [
        {"index": idx, "value": clean[idx], "z_score": round(z_scores[idx], 2)}
        for idx in outlier_idx
    ]
    return pd.DataFrame(rows)


def compute_trend_direction(
    values: Sequence[float],
    stability_pct: float = 5.0,
) -> str:
    """Return 'increase', 'decrease', or 'stable' based on first/last values."""
    if len(values) < 2:
        return "stable"
    change = pct_change(values[0], values[-1])
    if abs(change) <= stability_pct:
        return "stable"
    return "increase" if change > 0 else "decrease"


def safe_mean(values: Sequence[float]) -> float:
    """Return mean, handling empty sequences gracefully."""
    arr = [v for v in values if v is not None and not (isinstance(v, float) and np.isnan(v))]
    return float(np.mean(arr)) if arr else 0.0


def numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return the names of numeric columns in *df*."""
    return df.select_dtypes(include="number").columns.tolist()


def first_string_column(df: pd.DataFrame) -> Optional[str]:
    """Return the name of the first object/string column, or None."""
    obj_cols = df.select_dtypes(include="object").columns.tolist()
    return obj_cols[0] if obj_cols else None
