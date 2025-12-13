"""Video processing utilities."""

import os
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if it doesn't."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def clean_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up {file_path}: {e}")


def get_output_path(output_dir: str, filename: str, ensure_exists: bool = True) -> str:
    """Get full output path for a file."""
    if ensure_exists:
        ensure_directory(output_dir)
    return str(Path(output_dir) / filename)

