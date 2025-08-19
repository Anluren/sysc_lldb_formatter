#!/usr/bin/env python3
"""
Enum Pretty-Printer Examples for GDB

This module demonstrates how to create pretty-printers that can lookup
enum value names from their numeric values, making debugging much more
readable and informative.

Usage:
    In GDB, source this file:
    (gdb) source enum_pretty_printer.py
    
Author: SystemC LLDB Formatter Project
License: MIT
"""

import gdb
import gdb.printing


class EnumPrinter:
    """
    Generic pretty-printer for enum types that displays both name and value.
    
    This printer can automatically detect enum types and display them as
    "EnumName::VALUE_NAME(123)" instead of just showing the numeric value.
    """
    
    def __init__(self, val):
        """Initialize the enum printer with a GDB value object."""
        self.val = val
        self.type = val.type
    
    def to_string(self):
        """Return formatted string representation of the enum value."""
        try:
            # Get the numeric value
            numeric_value = int(self.val)
            
            # Try to find the enum name for this value
            enum_name = self.lookup_enum_name(numeric_value)
            
            if enum_name:
                return f"{self.type.name}::{enum_name}({numeric_value})"
            else:
                return f"{self.type.name}(<unknown:{numeric_value}>)"
                
        except Exception as e:
            return f"{self.type.name}(<error: {e}>)"
    
    def lookup_enum_name(self, value):
        """
        Lookup enum name from numeric value.
        
        Args:
            value (int): The numeric value to lookup
            
        Returns:
            str or None: The enum name if found, None otherwise
        """
        try:
            # Method 1: Use GDB's built-in enum field iteration
            for field in self.type.fields():
                if hasattr(field, 'enumval') and field.enumval == value:
                    return field.name
            
            # Method 2: Try direct type lookup (for some GDB versions)
            try:
                # This works for some enum types
                enum_val = gdb.Value(value).cast(self.type)
                return str(enum_val)
            except Exception:
                pass
                
        except Exception:
            pass
        
        return None
    
    def display_hint(self):
        """Return display hint for GDB."""
        return 'string'


class SystemCEnumPrinter:
    """
    Specialized pretty-printer for SystemC-specific enums.
    
    This handles common SystemC enums like sc_logic_value_t, sc_time_unit, etc.
    """
    
    # Define known SystemC enum mappings
    SYSTEMC_ENUMS = {
        'sc_dt::sc_logic_value_t': {
            0: 'SC_LOGIC_0',
            1: 'SC_LOGIC_1',
            2: 'SC_LOGIC_Z',
            3: 'SC_LOGIC_X'
        },
        'sc_core::sc_time_unit': {
            0: 'SC_FS',
            1: 'SC_PS',
            2: 'SC_NS',
            3: 'SC_US',
            4: 'SC_MS',
            5: 'SC_SEC'
        },
        'sc_core::sc_severity': {
            0: 'SC_INFO',
            1: 'SC_WARNING',
            2: 'SC_ERROR',
            3: 'SC_FATAL'
        }
    }
    
    def __init__(self, val):
        """Initialize the SystemC enum printer."""
        self.val = val
        self.type = val.type
        self.type_name = (str(self.type.name) if self.type.name
                          else str(self.type))
    
    def to_string(self):
        """Return formatted string representation of the SystemC enum."""
        try:
            numeric_value = int(self.val)
            
            # First try our known SystemC enum mappings
            enum_name = self.lookup_systemc_enum(numeric_value)
            
            # If not found, try generic enum lookup
            if not enum_name:
                enum_name = self.lookup_generic_enum(numeric_value)
            
            if enum_name:
                return f"{self.type_name}::{enum_name}({numeric_value})"
            else:
                return f"{self.type_name}(<unknown:{numeric_value}>)"
                
        except Exception as e:
            return f"{self.type_name}(<error: {e}>)"
    
    def lookup_systemc_enum(self, value):
        """Lookup SystemC enum name from our predefined mappings."""
        return self.SYSTEMC_ENUMS.get(self.type_name, {}).get(value)
    
    def lookup_generic_enum(self, value):
        """Fallback to generic enum lookup."""
        try:
            for field in self.type.fields():
                if hasattr(field, 'enumval') and field.enumval == value:
                    return field.name
        except Exception:
            pass
        return None
    
    def display_hint(self):
        """Return display hint for GDB."""
        return 'string'


class CustomEnumPrinter:
    """
    Example of a custom enum printer for user-defined enums.
    
    This shows how to create a printer for your own enum types
    with custom formatting and additional information.
    """
    
    def __init__(self, val):
        """Initialize the custom enum printer."""
        self.val = val
        self.type = val.type
    
    def to_string(self):
        """Return formatted string with additional enum information."""
        try:
            numeric_value = int(self.val)
            enum_name = self.lookup_enum_name(numeric_value)
            
            if enum_name:
                # Custom formatting with additional info
                description = self.get_enum_description(enum_name)
                if description:
                    return f"{enum_name}({numeric_value}) - {description}"
                else:
                    return f"{enum_name}({numeric_value})"
            else:
                return f"<invalid_enum_value:{numeric_value}>"
                
        except Exception as e:
            return f"<enum_error: {e}>"
    
    def lookup_enum_name(self, value):
        """Lookup enum name from value."""
        try:
            for field in self.type.fields():
                if hasattr(field, 'enumval') and field.enumval == value:
                    return field.name
        except Exception:
            pass
        return None
    
    def get_enum_description(self, enum_name):
        """
        Get human-readable description for enum values.
        
        This is where you can add custom descriptions for your enum values.
        """
        descriptions = {
            'STATE_IDLE': 'System is waiting for input',
            'STATE_PROCESSING': 'System is actively processing data',
            'STATE_ERROR': 'System encountered an error',
            'STATE_SHUTDOWN': 'System is shutting down'
        }
        return descriptions.get(enum_name)
    
    def display_hint(self):
        """Return display hint for GDB."""
        return 'string'


def build_enum_pretty_printer():
    """Build and return the enum pretty-printer collection."""
    pp = gdb.printing.RegexpCollectionPrettyPrinter("enums")
    
    # Register SystemC enum types
    pp.add_printer('sc_logic_value', r'^sc_dt::sc_logic_value_t$',
                   SystemCEnumPrinter)
    pp.add_printer('sc_time_unit', r'^sc_core::sc_time_unit$',
                   SystemCEnumPrinter)
    pp.add_printer('sc_severity', r'^sc_core::sc_severity$',
                   SystemCEnumPrinter)
    
    # Register generic enum printer for any enum type
    # Note: This is a catch-all that will match any enum type not already
    # handled
    pp.add_printer('generic_enum', r'^enum .*$', EnumPrinter)
    
    # Example: Register custom enum printer for specific user types
    pp.add_printer('my_state_enum', r'^MyStateEnum$', CustomEnumPrinter)
    
    return pp


class EnumDebugCommand(gdb.Command):
    """
    GDB command to analyze enum types and their values.
    
    Usage: enum_debug <variable_name>
    """
    
    def __init__(self):
        """Initialize the enum debug command."""
        super().__init__("enum_debug", gdb.COMMAND_USER)
    
    def invoke(self, argument, from_tty):
        """Execute the enum debug command."""
        del from_tty  # Unused parameter required by GDB API
        if not argument:
            print("Usage: enum_debug <variable_name>")
            return
        
        var_name = argument.strip()
        
        try:
            val = gdb.parse_and_eval(var_name)
            
            print(f"\n=== Enum Analysis: {var_name} ===")
            print(f"Type: {val.type}")
            print(f"Numeric value: {int(val)}")
            
            # Check if it's an enum type
            if val.type.code == gdb.TYPE_CODE_ENUM:
                print("✓ This is an enum type")
                
                # List all possible enum values
                print("\nPossible values:")
                for field in val.type.fields():
                    if hasattr(field, 'enumval'):
                        marker = "→" if field.enumval == int(val) else " "
                        print(f"  {marker} {field.name} = {field.enumval}")
                
                # Show formatted representation
                if str(val.type).startswith('sc_'):
                    printer = SystemCEnumPrinter(val)
                else:
                    printer = EnumPrinter(val)
                
                formatted = printer.to_string()
                print(f"\nFormatted: {formatted}")
                
            else:
                print("✗ This is not an enum type")
                print(f"Type code: {val.type.code}")
                
        except gdb.error as e:
            print(f"Error: {e}")


def register_enum_printers():
    """Register enum pretty-printers with GDB."""
    try:
        # Register the enum pretty-printer
        gdb.printing.register_pretty_printer(
            gdb.current_objfile(),
            build_enum_pretty_printer(),
            replace=True
        )
        
        # Register the debug command
        EnumDebugCommand()
        
        print("Enum pretty-printers loaded successfully!")
        print("Usage:")
        print("  - Enum variables will be automatically formatted")
        print("  - Use 'enum_debug <variable>' for detailed analysis")
        print("  - Supported: SystemC enums, generic enums, custom enums")
        
    except (gdb.error, ValueError, TypeError) as e:
        print(f"Error registering enum printers: {e}")


# Auto-register when the module is imported
if __name__ == "__main__":
    register_enum_printers()
else:
    register_enum_printers()
