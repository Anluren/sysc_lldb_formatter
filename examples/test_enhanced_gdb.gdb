# Enhanced GDB test script with Python support check
# Load the SystemC GDB formatter
source ../sysc_gdb_formatter.py

# Check Python support first
sc_python_check

# Set breakpoint at the return statement
break test_example.cpp:51

# Run the program
run

# Test a few variables with the formatter
echo \n=== Testing SystemC Formatters ===\n
print uint8_val
print int8_val
print single_bit

# Test the debug command
echo \n=== Testing sc_debug Command ===\n
sc_debug uint8_val

# Continue and exit
echo \n=== Test Complete ===\n
continue
quit
