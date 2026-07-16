"""Validation of the minimum pedestrian-segment dataset structure."""
from __future__ import annotations

from dataclasses import dataclass

from routing.exceptions import DatasetUnavailableError

REQUIRED_COLUMNS = frozenset({"origin", "destination", "length", "harassmentRisk"})


@dataclass(frozen=True)
class DatasetValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


class DatasetValidator:
    """Validates critical columns and values without mutating input rows."""

    @staticmethod
    def validate_rows(rows: list[dict[str, str]]) -> DatasetValidationResult:
        if not rows:
            return DatasetValidationResult(False, ("The source contains no rows.",))
        missing_columns = REQUIRED_COLUMNS.difference(rows[0])
        if missing_columns:
            column_list = ", ".join(sorted(missing_columns))
            return DatasetValidationResult(False, (f"Missing required columns: {column_list}.",))
        valid_rows = sum(1 for row in rows if DatasetValidator._has_valid_required_values(row))
        if not valid_rows:
            return DatasetValidationResult(False, ("The source contains no segments with valid values.",))
        return DatasetValidationResult(True, ())

    @staticmethod
    def validate_or_raise(rows: list[dict[str, str]]) -> None:
        validation_result = DatasetValidator.validate_rows(rows)
        if not validation_result.is_valid:
            raise DatasetUnavailableError(" ".join(validation_result.errors))

    @staticmethod
    def _has_valid_required_values(row: dict[str, str]) -> bool:
        try:
            risk = row["harassmentRisk"]
            if risk:
                float(risk)
            return bool(row["origin"] and row["destination"]) and float(row["length"]) > 0
        except (KeyError, TypeError, ValueError):
            return False
