# GDB test script for SystemC formatter
# Usage: gdb -x test_gdb.gdb ./test_example

# Load the SystemC GDB formatter
source ../sysc_gdb_formatter.py

# Set breakpoint at the return statement
break test_example.cpp:51

# Run the program
run

# Test automatic pretty-printing
echo \n=== Testing Automatic Pretty-Printing ===\n
print uint8_val
print int8_val
print uint16_val
print int16_val
print uint32_val
print int32_val
print single_bit
print single_bit_signed
print odd_width
print another_odd
print max_uint8
print min_int8
print max_int8

# Test the debug command for detailed analysis
echo \n=== Testing sc_debug Command ===\n
sc_debug uint8_val
sc_debug int8_val
sc_debug single_bit
sc_debug max_int8

# Continue and exit
echo \n=== Test Complete ===\n
continue
quit
