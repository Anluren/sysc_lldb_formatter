#!/usr/bin/env python3

import lldb

class SystemCFormatterBase:
    """
    Base formatter class for SystemC integer types in LLDB debugger.
    This class provides common functionality for formatting SystemC sc_int and sc_uint
    types by extracting their template width parameters and reading their raw values
    from memory. It handles both signed and unsigned integer types with proper
    sign extension and bit masking based on the declared width.
    The formatter works by analyzing the memory layout of SystemC objects and
    reading the actual integer values stored at a specific offset (+8 bytes)
    from the object's base address.
    Attributes:
        valobj: LLDB SBValue object representing the SystemC variable
        width: Template width parameter extracted from the type name
    Methods:
        extract_template_width(): Parses type name to get width (e.g., sc_uint<8> -> 8)
        get_raw_value(): Reads the actual integer value from object memory
        mask_value(): Applies width-based masking and sign extension
        is_signed(): Determines if the type is signed (sc_int) or unsigned (sc_uint)
    """
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
        """Get raw value from SystemC object using known memory layout.
        This method reads the actual value stored in a SystemC object by directly
        accessing memory at a known offset (+8 bytes from the base address). It
        handles both signed and unsigned integer types with proper bit width
        consideration.
        The method performs the following steps:
        1. Gets the base address of the SystemC object
        2. Calculates the value address by adding 8-byte offset
        3. Reads memory based on the data width (1, 2, 4, or 8 bytes)
        4. Converts bytes to integer with appropriate signedness
        Returns:
            int or None: The extracted integer value if successful, None if:
                - The object address is invalid
                - Memory read operation fails
                - Any exception occurs during processing
        Note:
            This implementation relies on specific memory layout knowledge of
            SystemC objects and uses little-endian byte order for interpretation.
            The width and signedness are determined by helper methods is_signed()
            and the width attribute.
        """
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
    """
    Formatter for SystemC sc_uint types in LLDB debugger.
    This formatter provides a custom display representation for SystemC sc_uint objects
    during debugging sessions. It inherits from SystemCFormatterBase and implements
    the necessary methods to format sc_uint values with proper width information and
    value masking.
    The formatter extracts the raw value from the sc_uint object, applies appropriate
    width masking, and presents it in a readable format: sc_uint<width>(value).
    Methods:
        __init__(valobj, internal_dict): Initialize the formatter with LLDB value object
        update(): Update method (currently no-op)
        has_children(): Returns False as sc_uint has no child elements to display
        get_value(): Returns formatted string representation of the sc_uint value
    Returns:
        Formatted string in the form "sc_uint<width>(value)" or error messages for
        invalid/unknown values.
    """
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
    """
    Formatter for SystemC sc_int types in LLDB debugger.
    This formatter provides a custom display representation for SystemC sc_int objects,
    showing the templated width and the actual integer value with proper masking and
    sign extension applied.
    The formatter inherits from SystemCFormatterBase and implements the required
    interface methods for LLDB type summaries. It displays sc_int values in the
    format: sc_int<width>(value)
    Attributes:
        Inherits all attributes from SystemCFormatterBase including valobj and width.
    Methods:
        update(): Required LLDB formatter method (no-op implementation).
        has_children(): Returns False as sc_int is displayed as a simple value.
        get_value(): Returns formatted string representation of the sc_int value.
    Example output:
        sc_int<8>(42)        - for a valid 8-bit signed integer
        sc_int<16>(<unknown>) - when value cannot be determined
        sc_int<32>(<error: ...>) - when an exception occurs during formatting
    """
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
    """
    Provides a summary representation for SystemC sc_uint objects in LLDB.

    This function serves as an LLDB summary provider that formats sc_uint values
    for display in the debugger. It creates an SCUintFormatter instance and
    retrieves the formatted value representation.

    Args:
        valobj: The LLDB value object representing the sc_uint instance
        internal_dict: Internal dictionary used by LLDB for caching and state

    Returns:
        str: A formatted string representation of the sc_uint value suitable
             for display in the LLDB debugger
    """
    formatter = SCUintFormatter(valobj, internal_dict)
    return formatter.get_value()

def sc_int_summary_provider(valobj, internal_dict):
    """
    Provides a summary representation for SystemC sc_int objects in LLDB.

    This function serves as an LLDB summary provider that creates a formatted
    string representation of SystemC sc_int values for display in the debugger.

    Args:
        valobj: The LLDB SBValue object representing the sc_int instance to format.
        internal_dict: Internal dictionary used by LLDB for caching and state management.

    Returns:
        str: A formatted string representation of the sc_int value suitable for
             display in LLDB's variable view or when printing the object.
    """
    formatter = SCIntFormatter(valobj, internal_dict)
    return formatter.get_value()

def sc_debug_command(debugger, command, result, internal_dict):
    """
    LLDB command to debug and analyze SystemC variables (sc_uint and sc_int types).
    This command provides detailed analysis of SystemC variables including their
    formatted values, raw values, width information, and memory layout.
    Args:
        debugger (lldb.SBDebugger): The LLDB debugger instance
        command (str): The variable name to analyze
        result (lldb.SBCommandReturnObject): Object to store command output
        internal_dict (dict): Internal dictionary for command state
    Usage:
        sc_debug <variable_name>
    Example:
        (lldb) sc_debug my_sc_uint_var
    Output includes:
        - Variable type information
        - Formatted value representation
        - Raw value data
        - Bit width of the SystemC type
        - Memory address and layout
        - Hexadecimal dump of value storage location
    Note:
        - Only supports sc_uint<> and sc_int<> SystemC types
        - Requires a valid debugging session with selected target, process, thread, and frame
        - Variable must be accessible in the current frame scope
    """
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
    """Initialize LLDB module with SystemC formatters and commands.
    This function is automatically called by LLDB when the module is loaded.
    It registers custom summary providers for SystemC data types and adds
    debug commands for enhanced SystemC debugging experience.
    Args:
        debugger: The LLDB debugger instance
        internal_dict: Internal dictionary for LLDB module state
    Returns:
        None
    Side Effects:
        - Registers summary providers for sc_uint and sc_int types
        - Adds 'sc_debug' command to LLDB command interface
        - Prints initialization success message and usage information
    """
    # Register summary providers
    debugger.HandleCommand('type summary add -F sysc_lldb_formatter.sc_uint_summary_provider "sc_dt::sc_uint<*>"')
    debugger.HandleCommand('type summary add -F sysc_lldb_formatter.sc_int_summary_provider "sc_dt::sc_int<*>"')
    
    # Register debug command
    debugger.HandleCommand('command script add -f sysc_lldb_formatter.sc_debug_command sc_debug')
    
    print("SystemC formatters loaded successfully!")
    print("Usage:")
    print("  - sc_uint and sc_int variables will be automatically formatted")
    print("  - Use 'sc_debug <variable>' for detailed analysis")
