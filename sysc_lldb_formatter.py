#!/usr/bin/env python3

import lldb

class SystemCFormatterBase:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.width = self.extract_template_width()
        
    def extract_template_width(self):
        """Extract template width from type name"""
        try:
            type_name = self.valobj.GetType().GetName()
            # Extract width from sc_uint<8> or sc_int<8>
            start = type_name.find('<')
            end = type_name.find('>')
            if start != -1 and end != -1:
                return int(type_name[start+1:end])
        except:
            pass
        return 64  # default width
    
    def get_raw_value(self):
        """Get raw value from SystemC object using known memory layout"""
        try:
            # Based on memory analysis, the actual value is stored at offset +8 bytes
            target = self.valobj.GetTarget()
            process = target.GetProcess()
            error = lldb.SBError()
            
            # Get the base address of the object
            base_addr = self.valobj.GetLoadAddress()
            if base_addr == lldb.LLDB_INVALID_ADDRESS:
                return None
                
            # Read 8 bytes from offset +8 (where we found the actual values)
            value_addr = base_addr + 8
            
            # For signed types, we need to handle sign extension properly
            if self.is_signed():
                # Read as signed based on width
                if self.width <= 8:
                    data = process.ReadMemory(value_addr, 1, error)
                    if error.Success() and len(data) >= 1:
                        value = int.from_bytes(data[:1], byteorder='little', signed=True)
                        return value
                elif self.width <= 16:
                    data = process.ReadMemory(value_addr, 2, error)
                    if error.Success() and len(data) >= 2:
                        value = int.from_bytes(data[:2], byteorder='little', signed=True)
                        return value
                elif self.width <= 32:
                    data = process.ReadMemory(value_addr, 4, error)
                    if error.Success() and len(data) >= 4:
                        value = int.from_bytes(data[:4], byteorder='little', signed=True)
                        return value
                else:
                    data = process.ReadMemory(value_addr, 8, error)
                    if error.Success() and len(data) >= 8:
                        value = int.from_bytes(data[:8], byteorder='little', signed=True)
                        return value
            else:
                # Read as unsigned
                if self.width <= 8:
                    data = process.ReadMemory(value_addr, 1, error)
                    if error.Success() and len(data) >= 1:
                        value = int.from_bytes(data[:1], byteorder='little', signed=False)
                        return value
                elif self.width <= 16:
                    data = process.ReadMemory(value_addr, 2, error)
                    if error.Success() and len(data) >= 2:
                        value = int.from_bytes(data[:2], byteorder='little', signed=False)
                        return value
                elif self.width <= 32:
                    data = process.ReadMemory(value_addr, 4, error)
                    if error.Success() and len(data) >= 4:
                        value = int.from_bytes(data[:4], byteorder='little', signed=False)
                        return value
                else:
                    data = process.ReadMemory(value_addr, 8, error)
                    if error.Success() and len(data) >= 8:
                        value = int.from_bytes(data[:8], byteorder='little', signed=False)
                        return value
                        
        except Exception as e:
            pass
        return None
    
    def mask_value(self, value):
        """Apply width mask to the value"""
        if value is None:
            return None
        if self.width < 64:
            mask = (1 << self.width) - 1
            value = value & mask
            # Handle sign extension for signed types
            if self.is_signed() and (value & (1 << (self.width - 1))):
                value = value - (1 << self.width)
        return value
    
    def is_signed(self):
        """Check if this is a signed type"""
        return "sc_int<" in self.valobj.GetType().GetName()

class SCUintFormatter(SystemCFormatterBase):
    def __init__(self, valobj, internal_dict):
        super().__init__(valobj, internal_dict)
        
    def update(self):
        pass
        
    def has_children(self):
        return False
        
    def get_value(self):
        try:
            raw_value = self.get_raw_value()
            if raw_value is not None:
                # Apply width masking
                masked_value = self.mask_value(raw_value)
                return f"sc_uint<{self.width}>({masked_value})"
            else:
                return f"sc_uint<{self.width}>(<unknown>)"
        except Exception as e:
            return f"sc_uint<{self.width}>(<error: {e}>)"

class SCIntFormatter(SystemCFormatterBase):
    def __init__(self, valobj, internal_dict):
        super().__init__(valobj, internal_dict)
        
    def update(self):
        pass
        
    def has_children(self):
        return False
        
    def get_value(self):
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

def sc_uint_summary_provider(valobj, internal_dict):
    formatter = SCUintFormatter(valobj, internal_dict)
    return formatter.get_value()

def sc_int_summary_provider(valobj, internal_dict):
    formatter = SCIntFormatter(valobj, internal_dict)
    return formatter.get_value()

def sc_debug_command(debugger, command, result, internal_dict):
    """Debug command to analyze SystemC variables with correct memory reading"""
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

# Register the formatters
def __lldb_init_module(debugger, internal_dict):
    # Register summary providers
    debugger.HandleCommand('type summary add -F sysc_lldb_formatter.sc_uint_summary_provider "sc_dt::sc_uint<*>"')
    debugger.HandleCommand('type summary add -F sysc_lldb_formatter.sc_int_summary_provider "sc_dt::sc_int<*>"')
    
    # Register debug command
    debugger.HandleCommand('command script add -f sysc_lldb_formatter.sc_debug_command sc_debug')
    
    print("SystemC formatters loaded successfully!")
    print("Usage:")
    print("  - sc_uint and sc_int variables will be automatically formatted")
    print("  - Use 'sc_debug <variable>' for detailed analysis")
