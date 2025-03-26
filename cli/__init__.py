"""
A CLI to help developers with AI-related tasks

This tool provides functionalities to count tokens in text, files, or directories.

It also includes an option to ingest curated data from VTEX repositories.
"""

from core.counttokens import TokenCounter
from .__version__ import __version__

__all__ = ['TokenCounter']