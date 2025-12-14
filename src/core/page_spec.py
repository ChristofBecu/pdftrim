"""Utilities for parsing page specifications and converting to page indices.

All user-facing page numbers are 1-based.
All internal indices returned by this module are 0-based.
"""

from __future__ import annotations

from dataclasses import dataclass


class PageSpecError(ValueError):
    """Raised when a page specification cannot be parsed or validated."""


@dataclass(frozen=True)
class DeleteSpecResult:
    """Normalized page deletion indices."""

    indices_0_based_desc: list[int]

    @property
    def count(self) -> int:
        return len(self.indices_0_based_desc)

    def as_1_based_sorted(self) -> list[int]:
        return sorted([i + 1 for i in self.indices_0_based_desc])


def compute_indices_to_delete(
        spec: str,
        *,
        page_count: int,
        invert_selection: bool = False,
) -> tuple[list[int], list[int] | None]:
        """Compute 0-based deletion indices from a delete or keep specification.

        When invert_selection is False:
            - spec is a delete specification
            - returns (indices_to_delete_desc, None)

        When invert_selection is True:
            - spec is a keep specification (keep only those pages)
            - returns (indices_to_delete_desc, keep_indices_desc)

        Both outputs are sorted descending for safe deletion.
        """

        parsed = parse_delete_spec(spec, page_count=page_count)

        if not invert_selection:
                return parsed.indices_0_based_desc, None

        keep_indices_desc = parsed.indices_0_based_desc
        keep_set = set(keep_indices_desc)

        # Descending, safe-to-delete order.
        indices_to_delete_desc = [i for i in range(page_count - 1, -1, -1) if i not in keep_set]
        return indices_to_delete_desc, keep_indices_desc


def _require_page_count(page_count: int) -> None:
    if page_count < 0:
        raise PageSpecError("page_count must be >= 0")


def _parse_positive_int(token: str, *, what: str) -> int:
    token = token.strip()
    if not token:
        raise PageSpecError(f"Empty {what}")
    if not token.isdigit():
        raise PageSpecError(f"Invalid {what}: '{token}'")
    value = int(token)
    if value < 1:
        raise PageSpecError(f"{what} must be >= 1")
    return value


def parse_delete_spec(spec: str, *, page_count: int) -> DeleteSpecResult:
    """Parse a delete specification like '1-4,7' into 0-based indices.

    Rules:
    - Comma-separated items
    - Item is either N or A-B (inclusive)
    - Page numbers are 1-based
    - All pages must be within 1..page_count
    - Duplicates are allowed but will be de-duplicated

    Returns indices sorted descending for safe deletion.
    """

    _require_page_count(page_count)

    spec = (spec or "").strip()
    if not spec:
        raise PageSpecError("Delete specification cannot be empty")

    if page_count == 0:
        raise PageSpecError("Cannot delete pages from an empty document")

    indices: set[int] = set()

    for raw_item in spec.split(","):
        item = raw_item.strip()
        if not item:
            raise PageSpecError("Invalid delete specification: empty item")

        if "-" in item:
            parts = item.split("-")
            if len(parts) != 2:
                raise PageSpecError(f"Invalid range token: '{item}'")
            start_1 = _parse_positive_int(parts[0], what="range start")
            end_1 = _parse_positive_int(parts[1], what="range end")
            if end_1 < start_1:
                raise PageSpecError(f"Invalid range '{item}': end < start")
            if start_1 > page_count or end_1 > page_count:
                raise PageSpecError(
                    f"Range '{item}' out of bounds (document has {page_count} pages)"
                )
            for page_1 in range(start_1, end_1 + 1):
                indices.add(page_1 - 1)
        else:
            page_1 = _parse_positive_int(item, what="page number")
            if page_1 > page_count:
                raise PageSpecError(
                    f"Page {page_1} out of bounds (document has {page_count} pages)"
                )
            indices.add(page_1 - 1)

    indices_desc = sorted(indices, reverse=True)
    return DeleteSpecResult(indices_0_based_desc=indices_desc)


def indices_before_page(*, before_page_1_based: int, page_count: int) -> list[int]:
    """Return 0-based indices for pages strictly before before_page_1_based."""

    _require_page_count(page_count)
    if page_count == 0:
        return []

    if before_page_1_based < 1:
        raise PageSpecError("before page must be >= 1")
    if before_page_1_based > page_count + 1:
        raise PageSpecError(
            f"before page {before_page_1_based} out of bounds (document has {page_count} pages)"
        )

    # before N => delete 1..N-1
    end_exclusive = min(before_page_1_based - 1, page_count)
    return list(range(end_exclusive - 1, -1, -1))


def indices_after_page(*, after_page_1_based: int, page_count: int) -> list[int]:
    """Return 0-based indices for pages strictly after after_page_1_based."""

    _require_page_count(page_count)
    if page_count == 0:
        return []

    if after_page_1_based < 1:
        raise PageSpecError("after page must be >= 1")
    if after_page_1_based > page_count:
        raise PageSpecError(
            f"after page {after_page_1_based} out of bounds (document has {page_count} pages)"
        )

    # after N => delete N+1..end
    start_0 = after_page_1_based  # 1-based N => 0-based N, so N+1 => (N)
    if start_0 >= page_count:
        return []

    return list(range(page_count - 1, start_0 - 1, -1))
