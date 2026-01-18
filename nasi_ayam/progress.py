"""Progress reporting for CLI feedback."""

from typing import Callable

ProgressCallback = Callable[[str, bool], None]
"""Callback type: (stage_name, is_starting) -> None"""
