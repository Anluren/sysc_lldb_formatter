<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SystemC LLDB Formatter Project Instructions

This project provides LLDB pretty-printers for SystemC data types, specifically `sc_uint<W>` and `sc_int<W>`.

## Key Project Context
- **Target**: LLDB debugger pretty-printers for SystemC types
- **Language**: Python 3.6+ (LLDB Python API)
- **Dependencies**: LLDB with Python scripting support
- **Architecture**: Memory-based value extraction due to incomplete debug symbols

## Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Include comprehensive docstrings for all classes and methods
- Handle errors gracefully with meaningful error messages

## Technical Considerations
- SystemC objects store actual values at memory offset +8 bytes from object base
- Different bit widths (8, 16, 32, 64) require different memory read sizes
- Signed types need proper sign extension and two's complement handling
- LLDB Python API requires careful error handling with SBError objects

## Testing Requirements
- Include example SystemC test programs
- Provide clear setup instructions for LLDB with Python support
- Document memory layout assumptions and validation methods
