import pytest

from src.core.page_spec import (
    PageSpecError,
    parse_delete_spec,
    indices_before_page,
    indices_after_page,
)


def test_parse_delete_spec_dedupes_and_sorts_desc() -> None:
    result = parse_delete_spec("1-3,2", page_count=5)
    assert result.indices_0_based_desc == [2, 1, 0]
    assert result.as_1_based_sorted() == [1, 2, 3]


@pytest.mark.parametrize(
    "spec,page_count",
    [
        ("", 5),
        ("   ", 5),
        ("1", 0),
        ("1,,2", 5),
        ("4-1", 10),
        ("1-", 10),
        ("-2", 10),
        ("abc", 10),
        ("1-99", 10),
        ("99", 10),
    ],
)
def test_parse_delete_spec_rejects_invalid(spec: str, page_count: int) -> None:
    with pytest.raises(PageSpecError):
        parse_delete_spec(spec, page_count=page_count)


def test_indices_before_page_basic() -> None:
    assert indices_before_page(before_page_1_based=1, page_count=5) == []
    assert indices_before_page(before_page_1_based=3, page_count=5) == [1, 0]


def test_indices_after_page_basic() -> None:
    assert indices_after_page(after_page_1_based=5, page_count=5) == []
    assert indices_after_page(after_page_1_based=3, page_count=5) == [4, 3]


@pytest.mark.parametrize(
    "before_page,page_count",
    [
        (0, 5),
        (7, 5),
    ],
)
def test_indices_before_page_bounds(before_page: int, page_count: int) -> None:
    with pytest.raises(PageSpecError):
        indices_before_page(before_page_1_based=before_page, page_count=page_count)


@pytest.mark.parametrize(
    "after_page,page_count",
    [
        (0, 5),
        (6, 5),
    ],
)
def test_indices_after_page_bounds(after_page: int, page_count: int) -> None:
    with pytest.raises(PageSpecError):
        indices_after_page(after_page_1_based=after_page, page_count=page_count)
