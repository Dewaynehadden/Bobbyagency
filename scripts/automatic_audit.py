"""Compatibility entry point for the current measured PageSpeed UI test."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('pagespeed_audit.py')), run_name='__main__')
