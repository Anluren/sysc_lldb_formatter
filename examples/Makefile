# Makefile for SystemC LLDB Formatter Examples
#
# This Makefile compiles the SystemC test examples for use with LLDB.
# Make sure SystemC is installed and SYSTEMC_HOME is set.

# SystemC configuration
SYSTEMC_HOME ?= /usr/local/systemc
SYSTEMC_INCLUDE = $(SYSTEMC_HOME)/include
SYSTEMC_LIB = $(SYSTEMC_HOME)/lib

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -g -Wall -Wextra
INCLUDES = -I$(SYSTEMC_INCLUDE)
LDFLAGS = -L$(SYSTEMC_LIB)
LIBS = -lsystemc

# Default target
.PHONY: all clean help

all: test_example

# Build the test example
test_example: test_example.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< $(LDFLAGS) $(LIBS) -o $@

# Clean build artifacts
clean:
	rm -f test_example

# Help target
help:
	@echo "SystemC LLDB Formatter Examples"
	@echo ""
	@echo "Targets:"
	@echo "  all         - Build all examples (default)"
	@echo "  test_example - Build the test example"
	@echo "  clean       - Remove build artifacts"
	@echo "  help        - Show this help"
	@echo ""
	@echo "Environment Variables:"
	@echo "  SYSTEMC_HOME - Path to SystemC installation (default: /usr/local/systemc)"
	@echo ""
	@echo "Usage:"
	@echo "  1. Set SYSTEMC_HOME to your SystemC installation"
	@echo "  2. Run 'make' to build the examples"
	@echo "  3. Debug with: lldb test_example"
	@echo "  4. In LLDB: command script import ../sysc_lldb_formatter"
