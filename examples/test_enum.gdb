# GDB test script for enum pretty-printing
# Usage: gdb -x test_enum.gdb ./test_enum

# Compile the test program first:
# g++ -std=c++11 -g -O0 -o test_enum test_enum.cpp

# Load the enum pretty-printer
source ../enum_pretty_printer.py

# Set breakpoint at the return statement
break test_enum.cpp:32

# Run the program
run

# Test enum formatting
echo \n=== Testing Enum Pretty-Printing ===\n
print my_color
print my_state

# Test enum debug command
echo \n=== Testing enum_debug Command ===\n
enum_debug my_color
enum_debug my_state

# Test manual enum value lookup
echo \n=== Manual Enum Analysis ===\n
print (int)my_color
print (int)my_state

# Continue and exit
echo \n=== Test Complete ===\n
continue
quit
