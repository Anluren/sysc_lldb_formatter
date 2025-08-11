#!/usr/bin/env python3
"""
SystemC GDB Pretty-Printer

This module provides GDB pretty-printers for SystemC data types, specifically
sc_uint<W> and sc_int<W>. It extracts actual values from SystemC objects by
reading memory at specific offsets, solving the "incomplete type" problem
common when debugging SystemC applications.

Usage:
    In GDB, source this file:
    (gdb) source sysc_gdb_formatter.py
    
    Or add to your .gdbinit file:
    source /path/to/sysc_gdb_formatter.py

Author: SystemC LLDB Formatter Project
License: MIT
"""

import gdb
import gdb.printing
import struct


def check_gdb_python_support():
    """
    Check if GDB has Python scripting support enabled.
    
    This function verifies that the current GDB installation supports Python
    scripting, which is required for the SystemC pretty-printers to function.
    
    Returns:
        bool: True if Python support is available, False otherwise.
        
    Note:
        This function should be called before attempting to register
        pretty-printers to ensure compatibility. If Python support is not
        available, the formatters will not work and GDB will show error
        messages.
    """
    try:
        # Try to access a Python-specific GDB feature
        gdb.VERSION
        return True
    except AttributeError:
        return False


def print_python_support_info():
    """
    Print information about GDB Python support status.
    
    This function checks Python support and provides helpful information
    to the user about their GDB configuration and what to do if Python
    support is missing.
    """
    if check_gdb_python_support():
        print("✓ GDB Python support detected - SystemC formatters will work")
        try:
            import sys
            version = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"✓ Python version: {version}")
        except Exception:
            print("✓ Python version: unknown")
    else:
        print("✗ GDB Python support NOT detected")
        print("  SystemC formatters require GDB with Python scripting "
              "support.")
        print("  Please install a GDB version with Python support:")
        print("  - Ubuntu/Debian: apt install gdb")
        print("  - RedHat/CentOS: yum install gdb")
        print("  - macOS: brew install gdb")
        print("  - Or compile GDB with --with-python option")
        return False
    return True


class SystemCFormatterBase:
    """
    Base class for SystemC GDB pretty-printers.
    
    This class provides common functionality for formatting SystemC sc_int and
    sc_uint types by extracting their template width parameters and reading
    their raw values from memory at known offsets.
    
    The formatter works by analyzing the memory layout of SystemC objects and
    reading the actual integer values stored at a specific offset (+8 bytes)
    from the object's base address.
    """
    
    def __init__(self, val):
        """Initialize the formatter with a GDB value object."""
        self.val = val
        self.width = self.extract_template_width()
    
    def extract_template_width(self):
        """Extract template width from type name."""
        try:
            type_name = str(self.val.type)
            # Extract width from sc_uint<8> or sc_int<8>
            start = type_name.find('<')
            end = type_name.find('>')
            if start != -1 and end != -1:
                return int(type_name[start+1:end])
        except (ValueError, AttributeError):
            pass
        return 64  # default width
    
    def get_raw_value(self):
        """
        Get raw value from SystemC object using known memory layout.
        
        This method reads the actual value stored in a SystemC object by
        directly accessing memory at a known offset (+8 bytes from the base
        address). It handles both signed and unsigned integer types with
        proper bit width consideration.
        
        Returns:
            int or None: The extracted integer value if successful, None if
                        memory read fails or address is invalid.
        """
        try:
            # Get the address of the object
            addr = self.val.address
            if addr is None:
                return None
            
            # Calculate the value address (base + 8 bytes offset)
            value_addr = int(addr) + 8
            
            # Determine how many bytes to read based on width
            if self.width <= 8:
                bytes_to_read = 1
                format_char = 'b' if self.is_signed() else 'B'
            elif self.width <= 16:
                bytes_to_read = 2
                format_char = 'h' if self.is_signed() else 'H'
            elif self.width <= 32:
                bytes_to_read = 4
                format_char = 'i' if self.is_signed() else 'I'
            else:
                bytes_to_read = 8
                format_char = 'q' if self.is_signed() else 'Q'
            
            # Read memory from the calculated address
            inferior = gdb.selected_inferior()
            memory = inferior.read_memory(value_addr, bytes_to_read)
            
            # Unpack the bytes into an integer (little-endian)
            value = struct.unpack('<' + format_char, memory)[0]
            return value
            
        except (gdb.MemoryError, gdb.error, struct.error, OverflowError):
            return None
    
    def mask_value(self, value):
        """Apply width mask and sign extension to the value."""
        if value is None:
            return None
        
        if self.width < 64:
            # Apply width mask
            mask = (1 << self.width) - 1
            value = value & mask
            
            # Handle sign extension for signed types
            if self.is_signed() and (value & (1 << (self.width - 1))):
                value = value - (1 << self.width)
        
        return value
    
    def is_signed(self):
        """Check if this is a signed type."""
        return "sc_int<" in str(self.val.type)


class SCUintPrinter(SystemCFormatterBase):
    """
    GDB pretty-printer for SystemC sc_uint types.
    
    This printer provides a custom display representation for SystemC sc_uint
    objects during GDB debugging sessions. It formats sc_uint values with
    proper width information and value masking.
    """
    
    def __init__(self, val):
        """Initialize the sc_uint printer."""
        super().__init__(val)
    
    def to_string(self):
        """Return formatted string representation of the sc_uint value."""
        try:
            raw_value = self.get_raw_value()
            if raw_value is not None:
                # Apply width masking (no sign extension for unsigned)
                masked_value = self.mask_value(raw_value)
                return f"sc_uint<{self.width}>({masked_value})"
            else:
                return f"sc_uint<{self.width}>(<unknown>)"
        except Exception as e:
            return f"sc_uint<{self.width}>(<error: {e}>)"
    
    def display_hint(self):
        """Return display hint for GDB."""
        return 'string'


class SCIntPrinter(SystemCFormatterBase):
    """
    GDB pretty-printer for SystemC sc_int types.
    
    This printer provides a custom display representation for SystemC sc_int
    objects, showing the templated width and the actual integer value with
    proper masking and sign extension applied.
    """
    
    def __init__(self, val):
        """Initialize the sc_int printer."""
        super().__init__(val)
    
    def to_string(self):
        """Return formatted string representation of the sc_int value."""
        try:
            raw_value = self.get_raw_value()
            if raw_value is not None:
                # Apply width masking and sign extension
                masked_value = self.mask_value(raw_value)
                return f"sc_int<{self.width}>({masked_value})"
            else:
                return f"sc_int<{self.width}>(<unknown>)"
        except Exception as e:
            return f"sc_int<{self.width}>(<error: {e}>)"
    
    def display_hint(self):
        """Return display hint for GDB."""
        return 'string'


def build_pretty_printer():
    """Build and return the SystemC pretty-printer."""
    pp = gdb.printing.RegexpCollectionPrettyPrinter("systemc")
    
    # Register printers for sc_uint and sc_int types
    # Match both sc_dt::sc_uint<N> and sc_uint<N> patterns
    pp.add_printer('sc_uint', r'^sc_dt::sc_uint<.*>$', SCUintPrinter)
    pp.add_printer('sc_uint_alt', r'^sc_uint<.*>$', SCUintPrinter)
    pp.add_printer('sc_int', r'^sc_dt::sc_int<.*>$', SCIntPrinter)
    pp.add_printer('sc_int_alt', r'^sc_int<.*>$', SCIntPrinter)
    
    return pp


class SystemCDebugCommand(gdb.Command):
    """
    GDB command to debug and analyze SystemC variables.
    
    This command provides detailed analysis of SystemC variables including
    their formatted values, raw values, width information, and memory layout.
    
    Usage: sc_debug <variable_name>
    """
    
    def __init__(self):
        """Initialize the SystemC debug command."""
        super().__init__("sc_debug", gdb.COMMAND_USER)
    
    def invoke(self, argument, from_tty):
        """Execute the sc_debug command."""
        if not argument:
            print("Usage: sc_debug <variable_name>")
            return
        
        var_name = argument.strip()
        
        try:
            # Try to evaluate the variable
            val = gdb.parse_and_eval(var_name)
            
            print(f"\n=== SystemC Variable Analysis: {var_name} ===")
            print(f"Type: {val.type}")
            
            type_name = str(val.type)
            
            # Create appropriate formatter
            if "sc_uint<" in type_name:
                formatter = SCUintPrinter(val)
            elif "sc_int<" in type_name:
                formatter = SCIntPrinter(val)
            else:
                print("Not a SystemC sc_uint or sc_int type")
                return
            
            # Get the formatted value
            formatted_value = formatter.to_string()
            print(f"Formatted: {formatted_value}")
            
            # Show raw value details
            raw_value = formatter.get_raw_value()
            print(f"Raw value: {raw_value}")
            print(f"Width: {formatter.width}")
            
            # Show memory layout
            if val.address is not None:
                addr = int(val.address)
                print(f"Address: 0x{addr:x}")
                
                # Read and display memory at offset +8 (where the value is stored)
                try:
                    value_addr = addr + 8
                    inferior = gdb.selected_inferior()
                    memory = inferior.read_memory(value_addr, 8)
                    # Convert memoryview to bytes for proper formatting
                    memory_bytes = bytes(memory)
                    hex_bytes = ' '.join(f'{b:02x}' for b in memory_bytes)
                    print(f"Value memory (+8): {hex_bytes}")
                except (gdb.MemoryError, gdb.error):
                    print("Could not read value memory")
            else:
                print("Address: <not available>")
                
        except gdb.error as e:
            print(f"Error: {e}")


class SystemCPythonCheckCommand(gdb.Command):
    """
    GDB command to check Python support for SystemC formatters.
    
    This command verifies that GDB has proper Python scripting support
    and provides diagnostic information about the SystemC formatter
    environment.
    
    Usage: sc_python_check
    """
    
    def __init__(self):
        """Initialize the Python check command."""
        super().__init__("sc_python_check", gdb.COMMAND_USER)
    
    def invoke(self, argument, from_tty):
        """Execute the Python support check command."""
        print("\n=== SystemC GDB Python Support Check ===")
        
        # Check basic Python support
        if not print_python_support_info():
            return
        
        # Check GDB version
        try:
            print(f"✓ GDB version: {gdb.VERSION}")
        except Exception:
            print("✓ GDB version: unknown")
        
        # Check if pretty-printers are registered
        try:
            objfile = gdb.current_objfile()
            if objfile:
                print("✓ Object file available for pretty-printer registration")
            else:
                print("⚠ No current object file (load a program first)")
        except Exception as e:
            print(f"⚠ Object file check failed: {e}")
        
        # Check SystemC formatter availability
        try:
            pp = build_pretty_printer()
            print("✓ SystemC pretty-printers can be built")
            print(f"✓ Registered printers: {len(pp.subprinters)} types")
        except Exception as e:
            print(f"✗ Error building pretty-printers: {e}")
        
        print("\nSystemC formatter environment looks good!")
        print("Usage: source sysc_gdb_formatter.py to load formatters")


# Register the pretty-printers and commands
def register_systemc_printers():
    """
    Register SystemC pretty-printers with GDB.
    
    This function sets up the SystemC debugging environment by:
    1. Checking for GDB Python support
    2. Registering pretty-printers for SystemC data types with GDB
    3. Registering custom debug commands for SystemC analysis
    4. Providing user feedback on successful registration
    
    The function registers pretty-printers for automatic formatting of SystemC
    types like sc_uint and sc_int, and adds a custom 'sc_debug' command for
    detailed variable analysis.
    
    Note:
        This function should be called once during GDB initialization to enable
        SystemC-specific debugging features.
        
    Raises:
        Exception: If GDB pretty-printer registration fails or if the current
                  object file is not available.
    """
    # Check Python support first
    if not check_gdb_python_support():
        print_python_support_info()
        return
    
    try:
        # Register the pretty-printer
        gdb.printing.register_pretty_printer(
            gdb.current_objfile(),
            build_pretty_printer(),
            replace=True
        )
        
        # Register the debug command
        SystemCDebugCommand()
        
        # Register the Python check command
        SystemCPythonCheckCommand()
        
        print("SystemC GDB formatters loaded successfully!")
        print_python_support_info()
        print("Usage:")
        print("  - sc_uint and sc_int variables will be automatically "
              "formatted")
        print("  - Use 'sc_debug <variable>' for detailed analysis")
        print("  - Use 'sc_python_check' to verify Python support")
        
    except Exception as e:
        print(f"Error registering SystemC formatters: {e}")
        print("This may happen if:")
        print("  - No object file is currently loaded")
        print("  - GDB Python support is incomplete")
        print("  - Try loading after running your program")


# Auto-register when the module is imported
register_systemc_printers()
