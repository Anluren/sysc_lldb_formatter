# Enum Pretty-Printing with GDB

## Overview

GDB pretty-printers can automatically lookup enum value names from their numeric values, making debugging much more readable. Instead of seeing cryptic numbers like `10`, you'll see meaningful names like `STATE_PROCESSING(10)`.

## How It Works

The enum pretty-printer works by:

1. **Detecting enum types** - Automatically identifies when a variable is an enum
2. **Reading numeric value** - Gets the actual integer value stored
3. **Looking up name** - Uses GDB's type information to find the corresponding enum name
4. **Formatting output** - Displays both name and value: `EnumName::VALUE_NAME(123)`

## Usage Examples

### Basic Enum Formatting

```cpp
enum State {
    STATE_IDLE = 0,
    STATE_PROCESSING = 10,
    STATE_ERROR = 20
};

State current_state = STATE_PROCESSING;
```

**Without pretty-printer:**
```bash
(gdb) print current_state
$1 = 10
```

**With pretty-printer:**
```bash
(gdb) print current_state
$1 = State::STATE_PROCESSING(10)
```

### SystemC Enum Support

```cpp
#include <systemc.h>
using namespace sc_dt;

sc_logic_value_t logic_val = SC_LOGIC_1;
```

**With SystemC enum printer:**
```bash
(gdb) print logic_val
$1 = sc_dt::sc_logic_value_t::SC_LOGIC_1(1)
```

### Enum Class Support

```cpp
enum class Color {
    RED = 0,
    GREEN = 1,
    BLUE = 2
};

Color my_color = Color::BLUE;
```

**Formatted output:**
```bash
(gdb) print my_color
$1 = Color::BLUE(2)
```

## Setup Instructions

### 1. Load the Enum Pretty-Printer

```bash
# In GDB session
(gdb) source enum_pretty_printer.py

# Or add to ~/.gdbinit for automatic loading
echo "source /path/to/enum_pretty_printer.py" >> ~/.gdbinit
```

### 2. Verify Installation

```bash
(gdb) enum_debug my_enum_variable
```

Expected output:
```
=== Enum Analysis: my_enum_variable ===
Type: MyEnum
Numeric value: 5
✓ This is an enum type

Possible values:
    VALUE1 = 0
    VALUE2 = 3
  → VALUE3 = 5
    VALUE4 = 10

Formatted: MyEnum::VALUE3(5)
```

## Supported Enum Types

### 1. C-style Enums
```cpp
enum Direction {
    NORTH = 0,
    SOUTH = 1,
    EAST = 2,
    WEST = 3
};
```

### 2. C++11 Enum Classes
```cpp
enum class Status : int {
    SUCCESS = 0,
    ERROR = -1,
    PENDING = 100
};
```

### 3. SystemC Enums
```cpp
// Predefined SystemC enum mappings included:
sc_logic_value_t  // SC_LOGIC_0, SC_LOGIC_1, SC_LOGIC_Z, SC_LOGIC_X
sc_time_unit      // SC_FS, SC_PS, SC_NS, SC_US, SC_MS, SC_SEC
sc_severity       // SC_INFO, SC_WARNING, SC_ERROR, SC_FATAL
```

### 4. Custom Enum Types
```cpp
// Add your own enum mappings to the pretty-printer
enum MyCustomEnum {
    CUSTOM_VALUE1 = 100,
    CUSTOM_VALUE2 = 200
};
```

## Advanced Features

### 1. Enum Analysis Command

```bash
(gdb) enum_debug variable_name
```

Provides detailed information:
- Type information
- Numeric value
- All possible enum values
- Current value highlighted
- Formatted representation

### 2. Custom Enum Descriptions

The pretty-printer can include human-readable descriptions:

```cpp
enum SystemState {
    INIT,      // System initializing
    RUNNING,   // Normal operation
    ERROR      // Error state
};
```

**Enhanced output:**
```bash
(gdb) print state
$1 = RUNNING(1) - Normal operation
```

### 3. Error Handling

For invalid enum values:
```bash
(gdb) print corrupted_enum
$1 = MyEnum::<unknown:999>
```

## Integration with SystemC Formatters

Use both enum and SystemC formatters together:

```bash
# Load both formatters
(gdb) source sysc_gdb_formatter.py
(gdb) source enum_pretty_printer.py

# Now you get enhanced formatting for both SystemC types and enums
(gdb) print my_sc_uint_var    # Shows: sc_uint<8>(42)
(gdb) print my_enum_var       # Shows: State::RUNNING(1)
```

## Customization

### Adding Your Own Enum Types

Edit `enum_pretty_printer.py` and add your mappings:

```python
# Add to SYSTEMC_ENUMS dictionary or create new mappings
MY_CUSTOM_ENUMS = {
    'MyNamespace::MyEnum': {
        0: 'VALUE_ZERO',
        10: 'VALUE_TEN',
        20: 'VALUE_TWENTY'
    }
}
```

### Custom Formatting

Override the `to_string()` method for custom formatting:

```python
def to_string(self):
    numeric_value = int(self.val)
    enum_name = self.lookup_enum_name(numeric_value)
    
    # Custom format: just show the name without parentheses
    return f"{enum_name}" if enum_name else f"<invalid:{numeric_value}>"
```

## Troubleshooting

### Issue 1: Enums Show as Numbers

**Problem**: Enum values still display as numeric values.

**Solution**:
- Ensure the pretty-printer is loaded: `source enum_pretty_printer.py`
- Check if it's actually an enum: `enum_debug variable_name`
- Verify debug symbols: compile with `-g` flag

### Issue 2: "Not an enum type" Error

**Problem**: `enum_debug` reports variable is not an enum.

**Solution**:
- Check the variable type: `ptype variable_name`
- Ensure it's not typedef'd to an integer
- Try casting: `enum_debug (MyEnum)variable_name`

### Issue 3: Custom Enums Not Recognized

**Problem**: Your custom enums don't get formatted.

**Solution**:
- Add a regex pattern to match your enum type name
- Ensure the type name matches exactly
- Use `ptype` to see the exact type name GDB sees

## Performance Notes

- Enum lookup is fast (O(n) where n = number of enum values)
- Minimal memory overhead
- No impact on program execution speed
- Only active during debugging sessions

## Best Practices

1. **Compile with debug info**: Always use `-g` flag
2. **Use meaningful enum names**: Helps with debugging
3. **Document enum values**: Add comments explaining meaning
4. **Test with enum_debug**: Verify pretty-printer recognizes your enums
5. **Combine with other formatters**: Use alongside SystemC formatters for comprehensive debugging

## Example Debug Session

```bash
# Start debugging
gdb ./my_program

# Load formatters
(gdb) source enum_pretty_printer.py

# Set breakpoint and run
(gdb) break main
(gdb) run

# Check enum variables
(gdb) print current_state
$1 = State::PROCESSING(10)

# Analyze enum in detail
(gdb) enum_debug current_state
=== Enum Analysis: current_state ===
Type: State
Numeric value: 10
✓ This is an enum type
...

# Continue debugging with readable enum values
(gdb) continue
```

With enum pretty-printing, your debugging sessions become much more productive and easier to understand!
