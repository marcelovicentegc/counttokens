"""
CountTokens - A CLI tool for counting tokens in text datasets using tiktoken.

This package provides utilities for counting tokens in text, files, or entire directories
with support for various file formats.
"""

from .core import TokenCounter
from .__version__ import __version__

__all__ = ['TokenCounter']