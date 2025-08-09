# SystemC LLDB Formatters

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

LLDB pretty-printers for SystemC data types `sc_uint<W>` and `sc_int<W>`.

## Overview

When debugging SystemC applications with LLDB, the default representation of `sc_uint` and `sc_int` objects is not very helpful, typically showing incomplete type information. This package provides custom LLDB formatters that extract and display the actual values stored in these SystemC data types.

### Features

- ✅ **Automatic formatting** for `sc_uint<W>` and `sc_int<W>` types
- ✅ **All bit widths supported** (1-64 bits)
- ✅ **Memory-based value extraction** when debug symbols are incomplete  
- ✅ **Proper sign extension** for signed types
- ✅ **Debug command** for detailed analysis
- ✅ **Easy installation** and setup

### Before and After

**Before (default LLDB):**
```
(lldb) frame variable test_uint test_int
(sc_dt::sc_uint<8>) test_uint = (sc_dt::sc_uint_base = <incomplete type>)
(sc_dt::sc_int<8>) test_int = (sc_dt::sc_int_base = <incomplete type>)
```

**After (with formatters):**
```
(lldb) frame variable test_uint test_int
(sc_dt::sc_uint<8>) test_uint = sc_uint<8>(66)
(sc_dt::sc_int<8>) test_int = sc_int<8>(-42)
```

## Requirements

- **LLDB with Python scripting support** (LLDB 10.0+)
- **SystemC 2.3.0+** (for testing)
- **Python 3.6+**

### Building LLDB with Python Support

Many system packages of LLDB lack Python scripting support. If you encounter import errors, you may need to build LLDB from source:

```bash
# Clone LLVM project
git clone https://github.com/llvm/llvm-project.git
cd llvm-project

# Configure with Python support
cmake -S llvm -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_PROJECTS="clang;lldb" \
  -DLLDB_ENABLE_PYTHON=ON \
  -DLLDB_ENABLE_LIBEDIT=ON

# Build (this takes a while)
ninja -C build

# Install
sudo ninja -C build install
```

## Installation

### Option 1: Direct Download

```bash
# Clone the repository
git clone https://github.com/your-username/sysc_lldb_formatter.git
cd sysc_lldb_formatter

# The formatters are ready to use!
```

### Option 2: Python Package (Development)

```bash
# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install sysc-lldb-formatter
```

## Usage

### Basic Usage

1. **Load the formatters in LLDB:**
   ```bash
   (lldb) command script import /path/to/sysc_lldb_formatter
   ```

2. **Set breakpoints and debug as usual:**
   ```bash
   (lldb) breakpoint set --name sc_main
   (lldb) run
   (lldb) frame variable
   ```

3. **SystemC variables will now display their actual values!**

### Advanced Usage

**Detailed variable analysis:**
```bash
(lldb) sc_debug my_variable
```

**Manual formatting (if needed):**
```python
# In LLDB Python console
(lldb) script
>>> import sysc_lldb_formatter
>>> # Formatters are now available
```

### Example Session

```bash
$ lldb ./test_example
(lldb) command script import sysc_lldb_formatter
SystemC LLDB formatters loaded successfully!
Usage:
  - sc_uint and sc_int variables will be automatically formatted
  - Use 'sc_debug <variable>' for detailed analysis
  - Supports all bit widths: sc_uint<8>, sc_int<32>, etc.

(lldb) breakpoint set --name sc_main
(lldb) run
(lldb) frame variable uint8_val int8_val
(sc_dt::sc_uint<8>) uint8_val = sc_uint<8>(66)
(sc_dt::sc_int<8>) int8_val = sc_int<8>(-42)

(lldb) sc_debug uint8_val
=== SystemC Variable Analysis: uint8_val ===
Type: sc_dt::sc_uint<8>
Formatted: sc_uint<8>(66)
Raw value: 66
Width: 8
Signed: False
Address: 0x7fffffffd680
Value memory (+8): 42 00 00 00 00 00 00 00
```

## Examples

The `examples/` directory contains a complete test program:

```bash
cd examples/
make  # Requires SystemC installation
lldb test_example
```

## How It Works

### Memory Layout Analysis

SystemC objects store their actual values at a fixed memory offset from the object base address. Through analysis of the SystemC library, we determined that:

- **Actual values** are stored at **offset +8 bytes** from object base
- **Different bit widths** require different memory read sizes
- **Signed types** need proper two's complement interpretation

### Implementation Strategy

1. **Extract template width** from type name (`sc_uint<8>` → width = 8)
2. **Read memory directly** at the known offset (+8 bytes)
3. **Apply width masking** and sign extension as needed
4. **Format for display** in a human-readable format

This approach works even when debug symbols are incomplete or missing.

## Supported Types

| SystemC Type | Description | Example Values |
|--------------|-------------|----------------|
| `sc_uint<W>` | Unsigned integer, W bits | `sc_uint<8>(255)` |
| `sc_int<W>`  | Signed integer, W bits | `sc_int<8>(-128)` |

**Supported bit widths:** 1, 2, 3, ..., 64 bits

## Troubleshooting

### "ModuleNotFoundError: No module named 'lldb'"

Your LLDB installation lacks Python scripting support. You need to:
1. Build LLDB from source with Python support (see Requirements section)
2. Or use a different LLDB distribution that includes Python

### "Variable not found" or "No valid target"

Make sure you:
1. Have a running debug session (`run` command)
2. Are stopped at a breakpoint where the variable is in scope
3. Use the correct variable name

### Values appear incorrect

The formatters assume the standard SystemC memory layout. If you're using:
- A heavily modified SystemC version
- Custom sc_uint/sc_int implementations
- Cross-compilation with different architectures

You may need to adjust the memory offset in the formatter code.

## Development

### Running Tests

```bash
# Build example program
cd examples/
make

# Test with LLDB
lldb test_example
(lldb) command script import ../sysc_lldb_formatter
(lldb) breakpoint set --line 45  # Return statement
(lldb) run
(lldb) frame variable
```

### Code Structure

```
sysc_lldb_formatter/
├── sysc_lldb_formatter/    # Main package
│   ├── __init__.py         # Package initialization
│   └── formatters.py       # Core formatter implementations
├── examples/               # Test examples
│   ├── test_example.cpp    # SystemC test program
│   └── Makefile           # Build configuration
├── docs/                   # Documentation
├── setup.py               # Package setup
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- SystemC community for the excellent hardware description library
- LLVM/LLDB developers for the powerful debugging infrastructure
- Contributors and testers who helped improve the formatters

## Related Projects

- [SystemC](https://systemc.org/) - The SystemC hardware description language
- [LLDB](https://lldb.llvm.org/) - The LLVM debugger
- [GDB SystemC Pretty Printers](https://github.com/accellera-official/systemc/tree/master/docs) - Similar project for GDB
