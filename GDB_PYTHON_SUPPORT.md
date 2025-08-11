# GDB Python Support Guide

## Overview

This document explains GDB Python support requirements for the SystemC formatters, how to check if your GDB installation has Python support, and how to troubleshoot common issues.

## What is GDB Python Support?

GDB Python support allows you to extend GDB's functionality using Python scripts. The SystemC formatters rely on this feature to:

- Register custom pretty-printers for SystemC data types
- Access GDB's internal APIs for memory reading and type inspection
- Provide custom commands like `sc_debug` and `sc_python_check`
- Format SystemC variables automatically during debugging

## Checking Python Support

### Quick Check

Use the built-in command in the SystemC formatter:

```bash
# Load the formatter
(gdb) source sysc_gdb_formatter.py

# Check Python support
(gdb) sc_python_check
```

Expected output with Python support:
```
=== SystemC GDB Python Support Check ===
✓ GDB Python support detected - SystemC formatters will work
✓ Python version: 3.10
✓ GDB version: 12.1
✓ Object file available for pretty-printer registration
✓ SystemC pretty-printers can be built
✓ Registered printers: 4 types

SystemC formatter environment looks good!
```

### Manual Check

You can also check manually:

```bash
# Start GDB
gdb

# Try Python command
(gdb) python print("Python support works!")
```

If Python support is available, you'll see:
```
Python support works!
```

If not available, you'll see an error like:
```
Undefined command: "python".  Try "help".
```

## Installation Instructions

### Ubuntu/Debian

Most modern Ubuntu/Debian installations include GDB with Python support by default:

```bash
# Install GDB (usually includes Python support)
sudo apt update
sudo apt install gdb

# Verify installation
gdb --version
gdb -batch -ex "python print('Python works')" -ex "quit"
```

### RedHat/CentOS/Fedora

```bash
# RHEL/CentOS
sudo yum install gdb
# or for newer versions
sudo dnf install gdb

# Verify installation
gdb --version
gdb -batch -ex "python print('Python works')" -ex "quit"
```

### macOS

Using Homebrew (recommended):

```bash
# Install GDB with Python support
brew install gdb

# Note: You may need to sign the GDB binary for macOS security
# Follow instructions from: brew info gdb

# Verify installation
gdb --version
gdb -batch -ex "python print('Python works')" -ex "quit"
```

### Building from Source

If your distribution doesn't provide GDB with Python support, you can build it:

```bash
# Download GDB source
wget https://ftp.gnu.org/gnu/gdb/gdb-12.1.tar.xz
tar -xf gdb-12.1.tar.xz
cd gdb-12.1

# Configure with Python support
./configure --with-python

# Build and install
make -j$(nproc)
sudo make install

# Verify Python support
gdb --version
gdb -batch -ex "python print('Python works')" -ex "quit"
```

## Common Issues and Solutions

### Issue 1: "Undefined command: python"

**Problem**: GDB was compiled without Python support.

**Solution**: 
- Install a GDB version with Python support (see installation instructions above)
- Or build GDB from source with `--with-python` configure option

### Issue 2: "No module named 'gdb'"

**Problem**: Python can't find the GDB module.

**Solution**:
- This usually means GDB's Python integration is broken
- Try reinstalling GDB
- Check if you're using the correct GDB binary (some systems have multiple versions)

### Issue 3: "Python Exception" when loading formatters

**Problem**: Python version incompatibility or missing dependencies.

**Diagnosis**:
```bash
(gdb) python
>import sys
>print(sys.version)
>import gdb
>print("GDB module loaded successfully")
>end
```

**Solution**:
- Ensure Python 3.6+ is being used
- Check that `struct` module is available
- Update GDB to a newer version

### Issue 4: Formatters don't work after loading

**Problem**: Pretty-printers not registered correctly.

**Diagnosis**:
```bash
(gdb) info pretty-printer
```

**Solution**:
- Ensure you have an object file loaded (`file your_program`)
- Try reloading the formatters after loading your program
- Check that your SystemC types match the expected patterns

## Python Version Compatibility

### Supported Python Versions

- **Python 3.6+**: Fully supported
- **Python 3.10+**: Recommended (best performance and features)
- **Python 2.7**: Not supported (deprecated)

### Checking Python Version in GDB

```bash
(gdb) python
>import sys
>print(f"Python {sys.version_info.major}.{sys.version_info.minor}")
>end
```

## Advanced Configuration

### Custom Python Paths

If GDB can't find your Python installation:

```bash
# Set Python path before starting GDB
export PYTHONPATH=/path/to/your/python/modules:$PYTHONPATH
gdb your_program
```

### GDB Init Files

Add to your `~/.gdbinit` file for automatic loading:

```bash
# Add SystemC formatter auto-loading
source /path/to/sysc_gdb_formatter.py

# Or conditionally load if file exists
python
import os
if os.path.exists('/path/to/sysc_gdb_formatter.py'):
    gdb.execute('source /path/to/sysc_gdb_formatter.py')
end
```

## Testing Your Setup

### Complete Test Script

Create `test_python_setup.gdb`:

```bash
# Test GDB Python support thoroughly

echo === Testing Basic Python Support ===\n
python print("✓ Python import works")

echo === Testing GDB Module ===\n
python
import gdb
print("✓ GDB module imported successfully")
print(f"✓ GDB version: {gdb.VERSION}")
end

echo === Testing SystemC Formatters ===\n
source sysc_gdb_formatter.py

echo === Running Comprehensive Check ===\n
sc_python_check

echo === All Tests Complete ===\n
quit
```

Run the test:

```bash
gdb -batch -x test_python_setup.gdb
```

## Integration with IDEs

### VS Code

Add to your `.vscode/launch.json`:

```json
{
    "name": "GDB with SystemC Formatters",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/your_program",
    "setupCommands": [
        {
            "description": "Enable pretty-printing",
            "text": "-enable-pretty-printing",
            "ignoreFailures": true
        },
        {
            "description": "Load SystemC formatters",
            "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
            "ignoreFailures": false
        }
    ]
}
```

### CLion

In CLion's GDB settings, add startup commands:

```bash
source /path/to/sysc_gdb_formatter.py
sc_python_check
```

## Performance Considerations

### Memory Usage

GDB with Python support uses more memory:
- Base GDB: ~10-20 MB
- GDB + Python: ~30-50 MB
- With SystemC formatters: +5-10 MB

### Startup Time

Python integration adds minimal startup overhead:
- Cold start: +100-200ms
- Warm start: +50-100ms

## Security Considerations

### Script Loading

Only load trusted Python scripts in GDB:

```bash
# Check script content before loading
cat sysc_gdb_formatter.py | less

# Load with verification
(gdb) source sysc_gdb_formatter.py
```

### Sandboxing

GDB Python scripts run with full debugger privileges. Be cautious with:
- Scripts from untrusted sources
- Automatic script loading in shared environments
- Scripts that modify system state

## Troubleshooting Checklist

When SystemC formatters don't work:

1. **Check Python support**: `(gdb) python print("test")`
2. **Verify GDB version**: Modern GDB (8.0+) recommended
3. **Check Python version**: Must be 3.6+
4. **Load object file**: `(gdb) file your_program`
5. **Run diagnostics**: `(gdb) sc_python_check`
6. **Check error messages**: Look for specific Python exceptions
7. **Test with simple case**: Try with minimal SystemC program

## Getting Help

### Documentation

- [GDB Python API Reference](https://sourceware.org/gdb/onlinedocs/gdb/Python.html)
- [GDB Pretty-Printing](https://sourceware.org/gdb/onlinedocs/gdb/Pretty-Printing.html)
- [SystemC Reference](https://systemc.org/)

### Community Support

- GDB mailing lists: [gdb@sourceware.org](mailto:gdb@sourceware.org)
- SystemC forums: [Accellera SystemC](https://forums.accellera.org/)
- Stack Overflow: Tag questions with `gdb`, `python`, `systemc`

### Project Support

- GitHub Issues: [sysc_lldb_formatter issues](https://github.com/Anluren/sysc_lldb_formatter/issues)
- Use `sc_python_check` output when reporting issues
- Include GDB and Python version information

---

## Summary

GDB Python support is essential for the SystemC formatters to work. Most modern Linux distributions include GDB with Python support by default. Use the provided diagnostic tools (`sc_python_check`) to verify your setup and troubleshoot any issues.

The formatters require:
- GDB 8.0+ (recommended 12.0+)
- Python 3.6+ (recommended 3.10+)
- GDB compiled with `--with-python`

For the best experience, use the latest versions of both GDB and Python available for your platform.
