#!/usr/bin/env python3
"""
Test script to demonstrate SystemC GDB pretty-printer usage.

This script provides a simple test case for the SystemC GDB formatter and
includes usage instructions for debugging SystemC applications with GDB.
"""

def create_test_systemc_program():
    """Create a simple SystemC test program for GDB debugging."""
    program_content = '''#include <systemc.h>
#include <iostream>

int main() {
    // Test various SystemC integer types
    sc_dt::sc_uint<8> uint8_val = 255;
    sc_dt::sc_uint<16> uint16_val = 65535;
    sc_dt::sc_uint<32> uint32_val = 4294967295U;
    
    sc_dt::sc_int<8> int8_val = -128;
    sc_dt::sc_int<16> int16_val = -32768;
    sc_dt::sc_int<32> int32_val = -2147483648;
    
    // Set some specific values for testing
    uint8_val = 42;
    uint16_val = 1337;
    uint32_val = 0xDEADBEEF;
    
    int8_val = -42;
    int16_val = -1337;
    int32_val = -12345;
    
    std::cout << "SystemC Test Program" << std::endl;
    std::cout << "uint8_val = " << uint8_val << std::endl;
    std::cout << "uint16_val = " << uint16_val << std::endl;
    std::cout << "uint32_val = " << uint32_val << std::endl;
    std::cout << "int8_val = " << int8_val << std::endl;
    std::cout << "int16_val = " << int16_val << std::endl;
    std::cout << "int32_val = " << int32_val << std::endl;
    
    return 0;  // Set breakpoint here for debugging
}'''
    
    with open('/home/dzheng/opensource/sysc_lldb_formatter/test_systemc_gdb.cpp', 'w') as f:
        f.write(program_content)

def create_gdb_script():
    """Create a GDB script for testing the formatter."""
    gdb_script = '''# GDB script to test SystemC formatters
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
'''
    
    with open('/home/dzheng/opensource/sysc_lldb_formatter/test_gdb_script.gdb', 'w') as f:
        f.write(gdb_script)

def create_makefile():
    """Create a Makefile for building the test program."""
    makefile_content = '''# Makefile for SystemC GDB formatter test

CXX = g++
CXXFLAGS = -std=c++11 -g -O0 -Wall
SYSTEMC_HOME ?= /usr/local/systemc
INCLUDES = -I$(SYSTEMC_HOME)/include
LDFLAGS = -L$(SYSTEMC_HOME)/lib-linux64 -lsystemc -lm

TARGET = test_systemc_gdb
SOURCE = test_systemc_gdb.cpp

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $< $(LDFLAGS)

test: $(TARGET)
	gdb -x test_gdb_script.gdb ./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: test clean

# Usage instructions:
# 1. Make sure SystemC is installed and SYSTEMC_HOME is set correctly
# 2. Build the test program: make
# 3. Run GDB test: make test
# 4. Or manually: gdb ./test_systemc_gdb
#    (gdb) source sysc_gdb_formatter.py
#    (gdb) break main
#    (gdb) run
#    (gdb) print uint8_val
#    (gdb) sc_debug uint8_val
'''
    
    with open('/home/dzheng/opensource/sysc_lldb_formatter/Makefile.gdb', 'w') as f:
        f.write(makefile_content)

if __name__ == "__main__":
    print("Creating SystemC GDB test files...")
    create_test_systemc_program()
    create_gdb_script()
    create_makefile()
    print("Test files created:")
    print("  - test_systemc_gdb.cpp: SystemC test program")
    print("  - test_gdb_script.gdb: GDB script for automated testing")
    print("  - Makefile.gdb: Build and test automation")
    print("\nTo test the GDB formatter:")
    print("1. Ensure SystemC is installed")
    print("2. Set SYSTEMC_HOME environment variable")
    print("3. Run: python3 test_gdb_setup.py")
    print("4. Run: make -f Makefile.gdb")
    print("5. Run: make -f Makefile.gdb test")
