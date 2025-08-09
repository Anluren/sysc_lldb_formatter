# SystemC LLDB Formatters - Detailed Usage Guide

## Installation and Setup

### Prerequisites

Before using the SystemC LLDB formatters, ensure you have:

1. **LLDB with Python scripting support**
2. **SystemC library** (for compiling test programs)
3. **Python 3.6+** (usually included with LLDB)

### Verifying LLDB Python Support

Test if your LLDB has Python support:

```bash
lldb
(lldb) script print("Python support works!")
```

If you see an error like "script command requires the Python scripting language", you need to build LLDB from source or use a different distribution.

### Loading the Formatters

#### Method 1: Direct Import (Recommended)

```bash
# In LLDB command line
(lldb) command script import /path/to/sysc_lldb_formatter
```

#### Method 2: Add to LLDB Init File

Add the import command to your `~/.lldbinit` file for automatic loading:

```bash
echo "command script import /path/to/sysc_lldb_formatter" >> ~/.lldbinit
```

#### Method 3: Project-Specific Loading

Create a `.lldbinit` file in your project directory:

```bash
# Project .lldbinit
command script import ./sysc_lldb_formatter
breakpoint set --name sc_main
```

## Debugging Workflow

### Basic Debugging Session

1. **Compile your SystemC program with debug symbols:**
   ```bash
   g++ -std=c++17 -g -I$SYSTEMC_HOME/include -L$SYSTEMC_HOME/lib \
       your_program.cpp -lsystemc -o your_program
   ```

2. **Start LLDB and load formatters:**
   ```bash
   lldb your_program
   (lldb) command script import sysc_lldb_formatter
   ```

3. **Set breakpoints and run:**
   ```bash
   (lldb) breakpoint set --name sc_main
   (lldb) run
   ```

4. **Examine variables:**
   ```bash
   (lldb) frame variable
   (lldb) print my_sc_uint
   ```

### Advanced Debugging Techniques

#### Stepping Through SystemC Code

```bash
# Step into SystemC methods
(lldb) step

# Step over SystemC calls
(lldb) next

# Continue to next SystemC event
(lldb) continue
```

#### Examining Different Variable Scopes

```bash
# Show local variables
(lldb) frame variable

# Show variables in specific frame
(lldb) frame select 2
(lldb) frame variable

# Show global variables
(lldb) target variable
```

#### Using the Debug Command

The `sc_debug` command provides detailed analysis:

```bash
(lldb) sc_debug my_variable

# Example output:
# === SystemC Variable Analysis: my_variable ===
# Type: sc_dt::sc_uint<8>
# Formatted: sc_uint<8>(66)
# Raw value: 66
# Width: 8
# Signed: False
# Address: 0x7fffffffd680
# Value memory (+8): 42 00 00 00 00 00 00 00
```

## Supported SystemC Types

### sc_uint<W> - Unsigned Integers

```cpp
sc_uint<1> bit_flag(1);          // sc_uint<1>(1)
sc_uint<8> byte_val(255);        // sc_uint<8>(255) 
sc_uint<16> word_val(65535);     // sc_uint<16>(65535)
sc_uint<32> dword_val(0xDEADBEEF); // sc_uint<32>(3735928559)
sc_uint<64> qword_val(0x123456789ABCDEF0); // sc_uint<64>(...)
```

### sc_int<W> - Signed Integers

```cpp
sc_int<1> sign_bit(-1);          // sc_int<1>(-1)
sc_int<8> sbyte_val(-128);       // sc_int<8>(-128)
sc_int<16> sword_val(-32768);    // sc_int<16>(-32768)
sc_int<32> sdword_val(-1000000); // sc_int<32>(-1000000)
sc_int<64> sqword_val(-9223372036854775808LL); // sc_int<64>(...)
```

### Arbitrary Bit Widths

The formatters support any bit width from 1 to 64:

```cpp
sc_uint<3> three_bits(7);        // sc_uint<3>(7)
sc_uint<13> thirteen_bits(4095); // sc_uint<13>(4095)
sc_int<7> seven_bits(-64);       // sc_int<7>(-64)
sc_int<15> fifteen_bits(-16384); // sc_int<15>(-16384)
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'lldb'"

**Cause:** LLDB lacks Python scripting support.

**Solutions:**
1. Build LLDB from source with Python support
2. Use LLDB from Xcode (macOS) or LLVM distribution
3. Install lldb-dev package on Ubuntu: `sudo apt install lldb-dev`

#### Issue: Variables show "<incomplete type>"

**Cause:** Debug symbols are missing or formatter isn't loaded.

**Solutions:**
1. Ensure you compiled with `-g` flag
2. Load the formatter: `command script import sysc_lldb_formatter`
3. Check if variable is in scope

#### Issue: Wrong values displayed

**Cause:** Memory layout assumption incorrect for your SystemC version.

**Solutions:**
1. Check SystemC version compatibility
2. Verify memory layout with `sc_debug` command
3. Report issue with SystemC version info

#### Issue: "No valid target" error

**Cause:** No active debugging session.

**Solutions:**
1. Start debugging: `lldb your_program`
2. Run the program: `run`
3. Ensure you're stopped at a breakpoint

### Debugging the Formatters

If the formatters aren't working correctly:

1. **Check if they're loaded:**
   ```bash
   (lldb) type summary list
   # Should show sc_dt::sc_uint<*> and sc_dt::sc_int<*>
   ```

2. **Test with known values:**
   ```cpp
   sc_uint<8> test_val(42);  // Should show sc_uint<8>(42)
   ```

3. **Use the debug command:**
   ```bash
   (lldb) sc_debug test_val
   ```

4. **Check memory manually:**
   ```bash
   (lldb) memory read --size 4 --count 4 `&test_val`
   ```

## Performance Considerations

### Memory Access Overhead

The formatters read memory directly, which has minimal overhead:
- **1-8 bytes read** per variable display
- **Cached by LLDB** for repeated access
- **No impact on program execution**

### Large Variable Sets

For programs with many SystemC variables:
- Formatters are **lazy-loaded** (only format when displayed)
- Use **selective variable display**: `frame variable specific_var`
- Consider **conditional breakpoints** to reduce noise

## Integration with IDEs

### Visual Studio Code

1. Install the CodeLLDB extension
2. Add to your launch.json:
   ```json
   {
     "type": "lldb",
     "request": "launch", 
     "program": "${workspaceFolder}/your_program",
     "initCommands": [
       "command script import ${workspaceFolder}/sysc_lldb_formatter"
     ]
   }
   ```

### CLion

1. Set up LLDB as debugger
2. Add init commands in Run Configuration:
   ```
   command script import /path/to/sysc_lldb_formatter
   ```

### Vim/Neovim

Use with debugging plugins like:
- [vimspector](https://github.com/puremourning/vimspector)
- [nvim-dap](https://github.com/mfussenegger/nvim-dap)

## Extending the Formatters

### Adding New Types

To support additional SystemC types (e.g., `sc_bv`, `sc_lv`):

1. **Create a new formatter class:**
   ```python
   class SCBitVectorFormatter(SystemCFormatterBase):
       def get_value(self):
           # Implementation for sc_bv
           pass
   ```

2. **Register the formatter:**
   ```python
   def __lldb_init_module(debugger, internal_dict):
       debugger.HandleCommand(
           'type summary add -F your_module.sc_bv_summary_provider "sc_dt::sc_bv<*>"'
       )
   ```

### Customizing Display Format

You can modify the display format in the formatter classes:

```python
# Current format: sc_uint<8>(66)
return f"sc_uint<{self.width}>({masked_value})"

# Hexadecimal format: sc_uint<8>(0x42)
return f"sc_uint<{self.width}>(0x{masked_value:x})"

# Binary format: sc_uint<8>(0b01000010)
return f"sc_uint<{self.width}>(0b{masked_value:0{self.width}b})"
```

## Best Practices

### Debugging Workflow

1. **Use meaningful variable names**
2. **Set strategic breakpoints** (before/after SystemC operations)
3. **Examine intermediate values** during complex calculations
4. **Use conditional breakpoints** for specific scenarios

### Performance Tips

1. **Compile with optimization disabled** (`-O0`) for debugging
2. **Use release builds** for performance testing
3. **Minimize formatter overhead** by selective variable examination

### Code Organization

1. **Separate debug and release builds**
2. **Use version control** for formatter configurations
3. **Document SystemC-specific debugging notes** in your project
