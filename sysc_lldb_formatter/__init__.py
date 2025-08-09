"""
SystemC LLDB Formatters

A Python package providing LLDB pretty-printers for SystemC data types.

This package contains formatters for:
- sc_uint<W>: Unsigned SystemC integers
- sc_int<W>: Signed SystemC integers

The formatters work by reading memory directly from SystemC objects,
which is necessary when debug symbols are incomplete.

Example usage:
    (lldb) command script import sysc_lldb_formatter
    (lldb) frame variable my_sc_uint
    (sc_dt::sc_uint<8>) my_sc_uint = sc_uint<8>(42)
"""

__version__ = "1.0.0"
__author__ = "SystemC LLDB Formatter Team"
__license__ = "MIT"

from .formatters import (
    SystemCFormatterBase,
    SCUintFormatter,
    SCIntFormatter,
    sc_uint_summary_provider,
    sc_int_summary_provider,
    sc_debug_command,
)

__all__ = [
    "SystemCFormatterBase",
    "SCUintFormatter", 
    "SCIntFormatter",
    "sc_uint_summary_provider",
    "sc_int_summary_provider",
    "sc_debug_command",
]
