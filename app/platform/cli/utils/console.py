"""Console output utilities for CLI."""

import sys
from typing import Optional


class Console:
    """Simple console output utility with emoji support."""

    @staticmethod
    def info(message: str, verbose: bool = True) -> None:
        """Print info message."""
        if verbose:
            print(f"[INFO] {message}")

    @staticmethod
    def success(message: str) -> None:
        """Print success message."""
        print(f"[OK] {message}")

    @staticmethod
    def warning(message: str) -> None:
        """Print warning message."""
        print(f"[WARN] {message}", file=sys.stderr)

    @staticmethod
    def error(message: str) -> None:
        """Print error message."""
        print(f"[ERROR] {message}", file=sys.stderr)

    @staticmethod
    def dry_run(message: str) -> None:
        """Print dry run message."""
        print(f"[DRY RUN] {message}")

    @staticmethod
    def table_header(columns: list[str], widths: Optional[list[int]] = None) -> None:
        """Print table header."""
        if widths is None:
            widths = [15] * len(columns)

        header = " | ".join(col.ljust(w) for col, w in zip(columns, widths))
        separator = "-+-".join("-" * w for w in widths)
        print(header)
        print(separator)

    @staticmethod
    def table_row(values: list[str], widths: Optional[list[int]] = None) -> None:
        """Print table row."""
        if widths is None:
            widths = [15] * len(values)

        row = " | ".join(str(val).ljust(w) for val, w in zip(values, widths))
        print(row)
