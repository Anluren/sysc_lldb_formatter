# SystemC Debugger Formatters

This project provides pretty-printers/formatters for SystemC data types in both **LLDB** and **GDB** debuggers. The formatters solve the common "incomplete type" problem when debugging SystemC applications by directly reading values from memory at known offsets.

## Supported Types

- `sc_dt::sc_uint<W>` - Unsigned SystemC integers with template width W
- `sc_dt::sc_int<W>` - Signed SystemC integers with template width W

## Features

- **Memory-based value extraction**: Reads actual values from SystemC object memory (+8 byte offset)
- **Template width detection**: Automatically extracts bit width from type names
- **Proper sign handling**: Correct sign extension for signed types and masking for specified widths
- **Debug commands**: Additional commands for detailed variable analysis
- **Cross-platform**: Works on Linux, macOS, and Windows (where SystemC is supported)

## Quick Start

### LLDB Formatter

1. **Load the formatter in LLDB:**
   ```bash
   (lldb) command script import sysc_lldb_formatter.py
   ```

2. **Debug your SystemC program:**
   ```bash
   lldb your_systemc_program
   (lldb) breakpoint set -n main
   (lldb) run
   (lldb) print my_sc_uint_var  # Automatically formatted
   (lldb) sc_debug my_sc_uint_var  # Detailed analysis
   ```

### GDB Formatter

1. **Load the formatter in GDB:**
   ```bash
   (gdb) source sysc_gdb_formatter.py
   ```

2. **Debug your SystemC program:**
   ```bash
   gdb your_systemc_program
   (gdb) break main
   (gdb) run
   (gdb) print my_sc_uint_var  # Automatically formatted
   (gdb) sc_debug my_sc_uint_var  # Detailed analysis
   ```

## Installation

### Option 1: Copy and Use (Recommended)

Simply copy the formatter files to your project directory and load them in your debugger:

```bash
# Copy the formatters
cp sysc_lldb_formatter.py /path/to/your/project/
cp sysc_gdb_formatter.py /path/to/your/project/

# Use in LLDB
(lldb) command script import sysc_lldb_formatter.py

# Use in GDB  
(gdb) source sysc_gdb_formatter.py
```

### Option 2: Global Installation

Add to your debugger configuration files for automatic loading:

**For LLDB** - Add to `~/.lldbinit`:
```python
command script import /path/to/sysc_lldb_formatter.py
```

**For GDB** - Add to `~/.gdbinit`:
```bash
source /path/to/sysc_gdb_formatter.py
```

## Usage Examples

### Basic Variable Inspection

```bash
# LLDB
(lldb) print my_uint8        # Output: sc_uint<8>(42)
(lldb) print my_int16        # Output: sc_int<16>(-1337)

# GDB  
(gdb) print my_uint8         # Output: sc_uint<8>(42)
(gdb) print my_int16         # Output: sc_int<16>(-1337)
```

### Detailed Analysis

```bash
# LLDB
(lldb) sc_debug my_uint8
=== SystemC Variable Analysis: my_uint8 ===
Type: sc_dt::sc_uint<8>
Formatted: sc_uint<8>(42)
Raw value: 42
Width: 8
Address: 0x7ffeec8b5a10
Value memory (+8): 2a 00 00 00 00 00 00 00

# GDB
(gdb) sc_debug my_uint8
=== SystemC Variable Analysis: my_uint8 ===
Type: sc_dt::sc_uint<8>
Formatted: sc_uint<8>(42)
Raw value: 42
Width: 8
Address: 0x7ffeec8b5a10
Value memory (+8): 2a 00 00 00 00 00 00 00
```

## Testing

### Test with Provided Examples

1. **Create test program:**
   ```bash
   python3 test_gdb_setup.py  # Creates test files
   ```

2. **Build and test (requires SystemC installation):**
   ```bash
   # Set SystemC path
   export SYSTEMC_HOME=/usr/local/systemc
   
   # Build test program
   make -f Makefile.gdb
   
   # Run automated GDB test
   make -f Makefile.gdb test
   ```

### Manual Testing

1. **Create a simple SystemC program:**
   ```cpp
   #include <systemc.h>
   #include <iostream>

   int main() {
       sc_dt::sc_uint<8> val = 42;
       sc_dt::sc_int<16> sval = -1337;
       
       std::cout << "val = " << val << std::endl;     // Set breakpoint here
       std::cout << "sval = " << sval << std::endl;
       
       return 0;
   }
   ```

2. **Compile with debug info:**
   ```bash
   g++ -std=c++11 -g -O0 -I$SYSTEMC_HOME/include \
       -L$SYSTEMC_HOME/lib-linux64 -lsystemc \
       -o test_program test_program.cpp
   ```

3. **Debug with formatters:**
   ```bash
   # LLDB
   lldb test_program
   (lldb) command script import sysc_lldb_formatter.py
   (lldb) b main
   (lldb) run
   (lldb) print val
   
   # GDB
   gdb test_program
   (gdb) source sysc_gdb_formatter.py
   (gdb) break main
   (gdb) run
   (gdb) print val
   ```

## Technical Details

### Memory Layout

SystemC objects store their actual values at a specific memory offset:
- **Base address**: Object's main address
- **Value location**: Base address + 8 bytes
- **Data types**: 1, 2, 4, or 8 bytes depending on width

### Width Handling

- **1-8 bits**: Read 1 byte
- **9-16 bits**: Read 2 bytes  
- **17-32 bits**: Read 4 bytes
- **33-64 bits**: Read 8 bytes

### Sign Extension

For signed types (`sc_int`), proper two's complement sign extension is applied based on the template width parameter.

## Troubleshooting

### Common Issues

1. **"Variable not found" errors:**
   - Ensure you're at a valid breakpoint with the variable in scope
   - Check that debug symbols are available (`-g` compile flag)

2. **"Memory read failed" errors:**
   - Variable might be optimized out (compile with `-O0`)
   - Object might not be properly initialized

3. **Incorrect values displayed:**
   - Verify SystemC version compatibility
   - Check that object memory layout matches expectations

### Debug Commands

Both formatters provide `sc_debug` commands for detailed analysis:

```bash
# Shows type info, raw values, memory layout, and hex dumps
(lldb) sc_debug variable_name
(gdb) sc_debug variable_name
```

## Dependencies

- **Python 3.6+**
- **LLDB with Python support** (for LLDB formatter)
- **GDB with Python support** (for GDB formatter)  
- **SystemC library** (for compilation/testing)

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code follows the project style guidelines
5. Submit a pull request

## Project Structure

```
sysc_lldb_formatter/
├── sysc_lldb_formatter.py    # LLDB formatter
├── sysc_gdb_formatter.py     # GDB formatter  
├── test_gdb_setup.py         # Test file generator
├── utilities/                # Network utilities
│   └── network_data.py       # Network packet parsing
├── PROJECT_SUMMARY.md        # Project overview
└── README_GDB.md             # This file
```
