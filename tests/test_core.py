"""Tests for DataNarrate core narrators."""

from __future__ import annotations

import pandas as pd
import pytest

from datanarrate.config import NarrativeConfig, Tone
from datanarrate.core import (
    ComparisonNarrator,
    DataStoryteller,
    OutlierNarrator,
    SummaryNarrator,
    TrendNarrator,
)
from datanarrate.utils import fmt_number, fmt_pct, pct_change


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def quarterly_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Revenue": [100, 120, 140, 123],
        "Expenses": [80, 85, 90, 88],
    })


@pytest.fixture()
def product_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Product": ["A", "A", "B", "B", "C", "C"],
        "Sales": [200, 220, 170, 180, 300, 310],
    })


@pytest.fixture()
def outlier_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Value": [10, 12, 11, 13, 12, 50, 11, 12, 10, 13, 11, 12],
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTrendNarrator:
    def test_increasing_trend(self, quarterly_df: pd.DataFrame) -> None:
        narrator = TrendNarrator(NarrativeConfig(tone=Tone.FORMAL))
        result = narrator.narrate(quarterly_df, "Revenue", "Quarter")
        assert len(result) == 1
        assert "increased" in result[0] or "stable" in result[0] or "decreased" in result[0]

    def test_executive_tone(self, quarterly_df: pd.DataFrame) -> None:
        narrator = TrendNarrator(NarrativeConfig(tone=Tone.EXECUTIVE))
        result = narrator.narrate(quarterly_df, "Revenue", "Quarter")
        assert len(result) >= 1
        # Executive tone should mention momentum or attention or steady
        assert any(
            word in result[0].lower()
            for word in ["momentum", "attention", "steady", "grew", "declined"]
        )


class TestComparisonNarrator:
    def test_comparison_output(self, product_df: pd.DataFrame) -> None:
        narrator = ComparisonNarrator(NarrativeConfig(tone=Tone.CASUAL))
        result = narrator.narrate(product_df, "Sales", "Product")
        assert len(result) >= 1
        # Product C has highest mean sales, should appear
        assert "C" in result[0]

    def test_comparison_formal(self, product_df: pd.DataFrame) -> None:
        narrator = ComparisonNarrator(NarrativeConfig(tone=Tone.FORMAL))
        result = narrator.narrate(product_df, "Sales", "Product")
        assert len(result) >= 1
        assert "outperformed" in result[0] or "performed similarly" in result[0]


class TestOutlierNarrator:
    def test_detects_spike(self, outlier_df: pd.DataFrame) -> None:
        narrator = OutlierNarrator(NarrativeConfig(tone=Tone.FORMAL, outlier_threshold=2.0))
        result = narrator.narrate(outlier_df, "Value", "Month")
        assert len(result) >= 1
        assert "Jun" in result[0]

    def test_no_outliers_when_uniform(self) -> None:
        df = pd.DataFrame({"X": [10, 10, 10, 10, 10]})
        narrator = OutlierNarrator()
        result = narrator.narrate(df, "X")
        assert result == []


class TestSummaryNarrator:
    def test_summary_contains_header(self, quarterly_df: pd.DataFrame) -> None:
        narrator = SummaryNarrator(NarrativeConfig(tone=Tone.EXECUTIVE))
        result = narrator.narrate(quarterly_df)
        assert len(result) >= 1
        assert "4" in result[0]  # 4 records


class TestDataStoryteller:
    def test_full_story(self, quarterly_df: pd.DataFrame) -> None:
        storyteller = DataStoryteller(NarrativeConfig(tone=Tone.FORMAL))
        story = storyteller.tell_story(quarterly_df, period_col="Quarter")
        assert len(story) >= 3  # summary header + at least 2 metric summaries

    def test_generate_report_markdown(self, quarterly_df: pd.DataFrame) -> None:
        storyteller = DataStoryteller(NarrativeConfig(tone=Tone.CASUAL))
        report = storyteller.generate_report(quarterly_df, title="Test Report")
        assert report.startswith("# Test Report")
        assert "DataNarrate" in report

    def test_load_csv(self, tmp_path) -> None:
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("a,b\n1,2\n3,4\n")
        df = DataStoryteller.load(csv_path)
        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]


class TestUtils:
    def test_fmt_number_large(self) -> None:
        assert "1.50M" in fmt_number(1_500_000)

    def test_fmt_pct(self) -> None:
        assert fmt_pct(23.456) == "23.5%"

    def test_pct_change_basic(self) -> None:
        assert pct_change(100, 123) == pytest.approx(23.0)

    def test_pct_change_zero(self) -> None:
        assert pct_change(0, 0) == 0.0
