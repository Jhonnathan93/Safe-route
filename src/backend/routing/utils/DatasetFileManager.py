"""Safe, centralized access to the pedestrian-segment CSV source."""
from __future__ import annotations

import csv
from pathlib import Path

from routing.exceptions import DatasetUnavailableError


class DatasetFileManager:
    """Namespace for stateless operations on the data file."""

    @staticmethod
    def get_dataset_path(dataset_path: str) -> Path:
        """Validates and returns the configured path for the active source."""
        resolved_path = Path(dataset_path).resolve()
        if not resolved_path.is_file():
            raise DatasetUnavailableError("The pedestrian-network source is unavailable.")
        return resolved_path

    @staticmethod
    def read_rows(dataset_path: str) -> list[dict[str, str]]:
        """Reads CSV rows without interpreting business rules."""
        try:
            with DatasetFileManager.get_dataset_path(dataset_path).open(encoding="utf-8", newline="") as csv_file:
                return list(csv.DictReader(csv_file, delimiter=";"))
        except (OSError, csv.Error) as error:
            raise DatasetUnavailableError("The pedestrian network could not be read.") from error
