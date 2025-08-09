#!/usr/bin/env python3
"""
SystemC LLDB Formatters

LLDB pretty-printers for SystemC data types sc_uint<W> and sc_int<W>.

This module provides formatters that can extract actual values from SystemC
objects by reading memory directly, which is necessary when debug symbols
are incomplete.

Author: Generated for SystemC debugging
License: MIT
"""

import lldb
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Type hints for LLDB types when not in actual LLDB environment
    SBValue = lldb.SBValue
    SBDebugger = lldb.SBDebugger  
    SBCommandReturnObject = lldb.SBCommandReturnObject
else:
    # For runtime when LLDB is available
    try:
        SBValue = lldb.SBValue
        SBDebugger = lldb.SBDebugger
        SBCommandReturnObject = lldb.SBCommandReturnObject
    except AttributeError:
        # Fallback when LLDB types aren't available
        SBValue = object
        SBDebugger = object 
        SBCommandReturnObject = object


class SystemCFormatterBase:
    """Base class for SystemC type formatters with memory access capabilities."""
    
    def __init__(self, valobj, internal_dict: dict):
        """Initialize the formatter with an LLDB value object.
        
        Args:
            valobj: The LLDB value object to format
            internal_dict: Internal dictionary for LLDB (unused)
        """
        self.valobj = valobj
        self.width = self.extract_template_width()
        
    def extract_template_width(self) -> int:
        """Extract template width from type name.
        
        Returns:
            The bit width of the SystemC type, defaults to 64 if not found
        """
        try:
            type_name = self.valobj.GetType().GetName()
            # Extract width from sc_uint<8> or sc_int<8>
            start = type_name.find('<')
            end = type_name.find('>')
            if start != -1 and end != -1:
                return int(type_name[start+1:end])
        except (ValueError, AttributeError):
            pass
        return 64  # default width
    
    def get_raw_value(self) -> Optional[int]:
        """Get raw value from SystemC object using known memory layout.
        
        Based on memory analysis, SystemC objects store their actual values
        at offset +8 bytes from the object base address.
        
        Returns:
            The raw integer value, or None if extraction failed
        """
        try:
            target = self.valobj.GetTarget()
            process = target.GetProcess()
            error = lldb.SBError()
            
            # Get the base address of the object
            base_addr = self.valobj.GetLoadAddress()
            if base_addr == lldb.LLDB_INVALID_ADDRESS:
                return None
                
            # Read from offset +8 (where actual values are stored)
            value_addr = base_addr + 8
            
            # Determine read size based on width
            if self.width <= 8:
                read_size = 1
            elif self.width <= 16:
                read_size = 2
            elif self.width <= 32:
                read_size = 4
            else:
                read_size = 8
            
            # Read memory
            data = process.ReadMemory(value_addr, read_size, error)
            if not error.Success() or len(data) < read_size:
                return None
            
            # Convert bytes to integer
            value = int.from_bytes(
                data[:read_size], 
                byteorder='little', 
                signed=self.is_signed()
            )
            return value
                        
        except Exception:
            pass
        return None
    
    def mask_value(self, value: Optional[int]) -> Optional[int]:
        """Apply width mask to the value and handle sign extension.
        
        Args:
            value: The raw value to mask
            
        Returns:
            The masked value with proper sign extension for signed types
        """
        if value is None:
            return None
            
        if self.width < 64:
            mask = (1 << self.width) - 1
            value = value & mask
            
            # Handle sign extension for signed types
            if self.is_signed() and (value & (1 << (self.width - 1))):
                value = value - (1 << self.width)
                
        return value
    
    def is_signed(self) -> bool:
        """Check if this is a signed type.
        
        Returns:
            True if this is an sc_int type, False for sc_uint
        """
        return "sc_int<" in self.valobj.GetType().GetName()


class SCUintFormatter(SystemCFormatterBase):
    """Formatter for SystemC sc_uint<W> types."""
    
    def __init__(self, valobj, internal_dict: dict):
        super().__init__(valobj, internal_dict)
        
    def update(self):
        """Called by LLDB when the value needs updating."""
        pass
        
    def has_children(self) -> bool:
        """Return whether this value has child elements."""
        return False
        
    def get_value(self) -> str:
        """Get the formatted string representation of the value.
        
        Returns:
            Formatted string like "sc_uint<8>(66)"
        """
        try:
            raw_value = self.get_raw_value()
            if raw_value is not None:
                masked_value = self.mask_value(raw_value)
                return f"sc_uint<{self.width}>({masked_value})"
            else:
                return f"sc_uint<{self.width}>(<unknown>)"
        except Exception as e:
            return f"sc_uint<{self.width}>(<error: {e}>)"


class SCIntFormatter(SystemCFormatterBase):
    """Formatter for SystemC sc_int<W> types."""
    
    def __init__(self, valobj, internal_dict: dict):
        super().__init__(valobj, internal_dict)
        
    def update(self):
        """Called by LLDB when the value needs updating."""
        pass
        
    def has_children(self) -> bool:
        """Return whether this value has child elements."""
        return False
        
    def get_value(self) -> str:
        """Get the formatted string representation of the value.
        
        Returns:
            Formatted string like "sc_int<8>(-42)"
        """
        try:
            raw_value = self.get_raw_value()
            if raw_value is not None:
                masked_value = self.mask_value(raw_value)
                return f"sc_int<{self.width}>({masked_value})"
            else:
                return f"sc_int<{self.width}>(<unknown>)"
        except Exception as e:
            return f"sc_int<{self.width}>(<error: {e}>)"


def sc_uint_summary_provider(valobj, internal_dict: dict) -> str:
    """LLDB summary provider function for sc_uint types."""
    formatter = SCUintFormatter(valobj, internal_dict)
    return formatter.get_value()


def sc_int_summary_provider(valobj, internal_dict: dict) -> str:
    """LLDB summary provider function for sc_int types."""
    formatter = SCIntFormatter(valobj, internal_dict)
    return formatter.get_value()


def sc_debug_command(debugger, command: str, 
                    result, internal_dict: dict):
    """Debug command to analyze SystemC variables in detail.
    
    Usage: sc_debug <variable_name>
    
    This command provides detailed analysis of SystemC variables including
    memory layout, raw values, and formatting information.
    """
    if not command:
        result.AppendMessage("Usage: sc_debug <variable_name>")
        return
    
    target = debugger.GetSelectedTarget()
    if not target.IsValid():
        result.AppendMessage("No valid target")
        return
    
    process = target.GetProcess()
    if not process.IsValid():
        result.AppendMessage("No valid process")
        return
    
    thread = process.GetSelectedThread()
    if not thread.IsValid():
        result.AppendMessage("No valid thread")
        return
    
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        result.AppendMessage("No valid frame")
        return
    
    var_name = command.strip()
    valobj = frame.FindVariable(var_name)
    
    if not valobj.IsValid():
        result.AppendMessage(f"Variable '{var_name}' not found")
        return
    
    result.AppendMessage(f"\n=== SystemC Variable Analysis: {var_name} ===")
    
    type_name = valobj.GetType().GetName()
    result.AppendMessage(f"Type: {type_name}")
    
    # Create appropriate formatter
    if "sc_uint<" in type_name:
        formatter = SCUintFormatter(valobj, {})
    elif "sc_int<" in type_name:
        formatter = SCIntFormatter(valobj, {})
    else:
        result.AppendMessage("Not a SystemC sc_uint or sc_int type")
        return
    
    # Get the formatted value
    formatted_value = formatter.get_value()
    result.AppendMessage(f"Formatted: {formatted_value}")
    
    # Show raw value details
    raw_value = formatter.get_raw_value()
    result.AppendMessage(f"Raw value: {raw_value}")
    result.AppendMessage(f"Width: {formatter.width}")
    result.AppendMessage(f"Signed: {formatter.is_signed()}")
    
    # Show memory layout
    base_addr = valobj.GetLoadAddress()
    if base_addr != lldb.LLDB_INVALID_ADDRESS:
        result.AppendMessage(f"Address: 0x{base_addr:x}")
        
        # Read and display memory at offset +8 (where the value is stored)
        error = lldb.SBError()
        value_addr = base_addr + 8
        data = process.ReadMemory(value_addr, 8, error)
        if error.Success():
            hex_bytes = ' '.join(f'{b:02x}' for b in data)
            result.AppendMessage(f"Value memory (+8): {hex_bytes}")


def __lldb_init_module(debugger, internal_dict: dict):
    """Initialize the LLDB module and register formatters.
    
    This function is called automatically when the module is imported by LLDB.
    """
    # Register summary providers for SystemC types
    debugger.HandleCommand(
        'type summary add -F sysc_lldb_formatter.formatters.sc_uint_summary_provider "sc_dt::sc_uint<*>"'
    )
    debugger.HandleCommand(
        'type summary add -F sysc_lldb_formatter.formatters.sc_int_summary_provider "sc_dt::sc_int<*>"'
    )
    
    # Register debug command
    debugger.HandleCommand(
        'command script add -f sysc_lldb_formatter.formatters.sc_debug_command sc_debug'
    )
    
    print("SystemC LLDB formatters loaded successfully!")
    print("Usage:")
    print("  - sc_uint and sc_int variables will be automatically formatted")
    print("  - Use 'sc_debug <variable>' for detailed analysis")
    print("  - Supports all bit widths: sc_uint<8>, sc_int<32>, etc.")
