"""GDPR Obfuscator - A Python library for obfuscating PII in CSV files."""

__version__ = "0.1.0"
__author__ = "GDPR Obfuscator Team"

from .core.obfuscator import gdpr_obfuscator

__all__ = ["gdpr_obfuscator"]