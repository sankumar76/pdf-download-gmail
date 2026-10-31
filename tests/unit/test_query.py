"""PGD-15 AC-4: the baseline Gmail query (FR-009, AA-01 widening)."""

from __future__ import annotations

import pytest

from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.query import baseline_query

pytestmark = pytest.mark.req("FR-009", "AC-4")


def test_the_query_widens_both_epoch_bounds_by_one_second_with_literal_values() -> None:
    # Asia/Kolkata, 2026-01-01..2026-01-31: S = 1767205800, E = 1769884200 (see test_daterange)
    date_range = DateRange(1767205800, 1769884200)

    assert baseline_query(date_range) == (
        "has:attachment filename:pdf after:1767205799 before:1769884201"
    )


def test_there_is_no_trailing_space_without_a_user_query() -> None:
    query = baseline_query(DateRange(1000, 2000))

    assert query == query.rstrip()
    assert query.endswith("before:2001")


@pytest.mark.parametrize("blank", ["", " ", "\t\n  "])
def test_a_blank_user_query_adds_nothing(blank: str) -> None:
    assert baseline_query(DateRange(1000, 2000), blank) == baseline_query(DateRange(1000, 2000))


def test_user_query_text_is_appended_after_one_space() -> None:
    query = baseline_query(DateRange(1000, 2000), "  from:invoices@example.com ")

    assert query == "has:attachment filename:pdf after:999 before:2001 from:invoices@example.com"


def test_bounds_are_plain_integers_not_floats() -> None:
    query = baseline_query(DateRange(1767205800, 1769884200))

    assert ".0" not in query
