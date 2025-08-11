# GDB script to test SystemC formatters
# Usage: gdb -x test_gdb_script.gdb ./test_program

# Load the SystemC formatter
source sysc_gdb_formatter.py

# Set a breakpoint at the return statement
break test_systemc_gdb.cpp:32

# Run the program
run

# Print variables with the formatter
print uint8_val
print uint16_val
print uint32_val
print int8_val
print int16_val
print int32_val

# Use the debug command for detailed analysis
sc_debug uint8_val
sc_debug int8_val

# Continue execution
continue
quit
