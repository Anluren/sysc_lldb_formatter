# Makefile for SystemC GDB formatter test

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
