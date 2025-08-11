# GDB Python Support Test Script
# Usage: gdb -batch -x test_python_setup.gdb

echo === SystemC GDB Python Support Test ===\n

echo === Testing Basic Python Support ===\n
python print("✓ Python import works")

echo === Testing GDB Module ===\n
python
import gdb
print("✓ GDB module imported successfully")
try:
    print(f"✓ GDB version: {gdb.VERSION}")
except:
    print("✓ GDB version: unknown")
end

echo === Testing Required Python Modules ===\n
python
try:
    import struct
    print("✓ struct module available")
except ImportError:
    print("✗ struct module missing")

try:
    import sys
    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    if sys.version_info >= (3, 6):
        print("✓ Python version is compatible")
    else:
        print("✗ Python version too old (need 3.6+)")
except:
    print("✗ Cannot determine Python version")
end

echo === Testing SystemC Formatters ===\n
python
try:
    # Test if we can import the formatter classes
    exec(open('sysc_gdb_formatter.py').read())
    print("✓ SystemC formatters loaded successfully")
except FileNotFoundError:
    print("⚠ sysc_gdb_formatter.py not found (run from project directory)")
except Exception as e:
    print(f"✗ Error loading formatters: {e}")
end

echo === Testing Pretty-Printer Registration ===\n
python
try:
    import gdb.printing
    pp = gdb.printing.RegexpCollectionPrettyPrinter("test")
    print("✓ Pretty-printer infrastructure available")
except Exception as e:
    print(f"✗ Pretty-printer error: {e}")
end

echo === Testing Memory Access ===\n
python
try:
    inferior = gdb.selected_inferior()
    print("✓ Inferior access works")
except Exception as e:
    print(f"⚠ Inferior access: {e} (normal if no program loaded)")
end

echo === Final Assessment ===\n
python
print("=== GDB Python Support Summary ===")
try:
    import sys, gdb
    python_ok = sys.version_info >= (3, 6)
    gdb_ok = hasattr(gdb, 'VERSION')
    
    print(f"Python 3.6+: {'✓' if python_ok else '✗'}")
    print(f"GDB Python API: {'✓' if gdb_ok else '✗'}")
    
    if python_ok and gdb_ok:
        print("✓ Your GDB setup should work with SystemC formatters!")
        print("  Next steps:")
        print("  1. Load a SystemC program: gdb your_program")
        print("  2. Source formatters: source sysc_gdb_formatter.py")
        print("  3. Set breakpoints and debug with formatted variables")
    else:
        print("✗ Your GDB setup needs attention:")
        if not python_ok:
            print("  - Upgrade Python to 3.6+")
        if not gdb_ok:
            print("  - Install GDB with Python support")
        print("  See GDB_PYTHON_SUPPORT.md for detailed instructions")
except Exception as e:
    print(f"✗ Setup verification failed: {e}")
end

echo === Test Complete ===\n
quit
