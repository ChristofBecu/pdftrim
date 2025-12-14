from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OperationType(str, Enum):
    SEARCH = "search"
    DELETE = "delete"
    BEFORE_AFTER = "before_after"

    @classmethod
    def from_string(cls, value: str) -> "OperationType":
        normalized = (value or "").strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"Unknown operation type: {value}")


@dataclass(frozen=True)
class OperationRequest:
    """Typed request object for workflow routing."""

    operation: OperationType
    input_path: Optional[str]
    is_batch_mode: bool
    output_dir: Optional[str] = None

    search_string: str = ""
    delete_spec: str = ""
    invert_selection: bool = False
    before_page: Optional[int] = None
    after_page: Optional[int] = None

    def validate(self) -> None:
        if self.operation == OperationType.SEARCH:
            if not self.search_string.strip():
                raise ValueError("Search string cannot be empty")
        elif self.operation == OperationType.DELETE:
            if not self.delete_spec.strip():
                if self.invert_selection:
                    raise ValueError("Keep specification cannot be empty")
                raise ValueError("Delete specification cannot be empty")
        elif self.operation == OperationType.BEFORE_AFTER:
            if self.before_page is None and self.after_page is None:
                raise ValueError("At least one of before_page or after_page must be provided")
            for value in (self.before_page, self.after_page):
                if value is not None and value < 1:
                    raise ValueError("before_page/after_page must be positive, 1-based page numbers")
        else:
            raise ValueError(f"Invalid operation type: {self.operation}")
