# Quick GDB Python Troubleshooting

## Problem: "Undefined command: python"

**Cause**: GDB compiled without Python support

**Quick Fix**:
```bash
# Ubuntu/Debian
sudo apt install gdb

# macOS
brew install gdb

# Test
gdb -batch -ex "python print('works')" -ex "quit"
```

## Problem: SystemC formatters don't load

**Cause**: Missing Python modules or wrong directory

**Quick Fix**:
```bash
# Check Python version
gdb -batch -ex "python import sys; print(sys.version)" -ex "quit"

# Run comprehensive test
gdb -batch -x test_python_setup.gdb

# Load from correct directory
cd /path/to/sysc_lldb_formatter
gdb your_program
(gdb) source sysc_gdb_formatter.py
```

## Problem: "No current object file"

**Cause**: Pretty-printers need a loaded program

**Quick Fix**:
```bash
gdb your_program          # Load program first
(gdb) source sysc_gdb_formatter.py
(gdb) break main
(gdb) run
```

## Problem: Variables show as "incomplete type"

**Cause**: Formatters not registered or SystemC types not recognized

**Quick Fix**:
```bash
(gdb) sc_python_check     # Verify setup
(gdb) info pretty-printer # Check registration
(gdb) sc_debug variable_name  # Detailed analysis
```

## Problem: Python exceptions when debugging

**Cause**: Memory access issues or unsupported SystemC version

**Quick Fix**:
```bash
# Check SystemC version compatibility
(gdb) sc_debug variable_name
# Look for specific error messages

# Verify memory layout
(gdb) print &variable_name
(gdb) x/8bx &variable_name + 8  # Check +8 offset manually
```

## Quick Test Commands

```bash
# Test 1: Basic Python
gdb -batch -ex "python print('Python works')" -ex "quit"

# Test 2: GDB Python API
gdb -batch -ex "python import gdb; print('GDB API works')" -ex "quit"

# Test 3: Complete setup
gdb -batch -x test_python_setup.gdb

# Test 4: With SystemC program
gdb your_program
(gdb) source sysc_gdb_formatter.py
(gdb) sc_python_check
```

## Installation One-Liners

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install gdb && gdb --version

# CentOS/RHEL
sudo yum install gdb && gdb --version

# macOS
brew install gdb && gdb --version

# Verify all platforms
gdb -batch -ex "python print('✓ Python support confirmed')" -ex "quit"
```

For detailed information, see `GDB_PYTHON_SUPPORT.md`.
