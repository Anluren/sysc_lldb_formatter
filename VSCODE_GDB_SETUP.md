# Using GDB Scripts with VS Code Launch Configurations

This guide explains how to configure VS Code to automatically load `.gdb` files when debugging C++ programs using GDB.

## Overview

VS Code can automatically load GDB scripts through the `launch.json` configuration file using the `setupCommands` section. This allows you to:

- Load custom GDB Python scripts
- Set up pretty-printers automatically
- Execute GDB commands before debugging starts
- Load custom debugging utilities and commands

## Basic Configuration

### 1. Launch Configuration Structure

```json
{
    "name": "Debug with GDB Script",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/examples/your_program",
    "args": [],
    "stopAtEntry": false,
    "cwd": "${workspaceFolder}/examples",
    "MIMode": "gdb",
    "miDebuggerPath": "/usr/bin/gdb",
    "setupCommands": [
        {
            "description": "Enable pretty-printing for gdb",
            "text": "-enable-pretty-printing",
            "ignoreFailures": true
        },
        {
            "description": "Load your GDB script",
            "text": "source your_script.gdb",
            "ignoreFailures": false
        }
    ],
    "preLaunchTask": "build-your-program"
}
```

### 2. Key Properties

- **`setupCommands`**: Array of GDB commands to run before debugging
- **`text`**: The actual GDB command to execute
- **`description`**: Human-readable description of the command
- **`ignoreFailures`**: Whether to continue if this command fails

## Loading Different Types of GDB Files

### 1. Loading Python Scripts

```json
{
    "description": "Load SystemC GDB formatter",
    "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
    "ignoreFailures": false
}
```

### 2. Loading GDB Command Files

```json
{
    "description": "Load test commands",
    "text": "source test_inheritance.gdb",
    "ignoreFailures": false
}
```

### 3. Loading Multiple Scripts

```json
"setupCommands": [
    {
        "description": "Enable pretty-printing for gdb",
        "text": "-enable-pretty-printing",
        "ignoreFailures": true
    },
    {
        "description": "Load SystemC formatter",
        "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
        "ignoreFailures": false
    },
    {
        "description": "Load enum printer",
        "text": "source ${workspaceFolder}/enum_pretty_printer.py",
        "ignoreFailures": false
    },
    {
        "description": "Load inheritance utilities",
        "text": "source inheritance_example.py",
        "ignoreFailures": true
    }
]
```

## Project-Specific Configurations

### SystemC Debugging

```json
{
    "name": "Debug SystemC with GDB",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/examples/test_example",
    "cwd": "${workspaceFolder}/examples",
    "MIMode": "gdb",
    "setupCommands": [
        {
            "description": "Enable pretty-printing",
            "text": "-enable-pretty-printing",
            "ignoreFailures": true
        },
        {
            "description": "Load SystemC GDB formatter",
            "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
            "ignoreFailures": false
        },
        {
            "description": "Load enum pretty printer",
            "text": "source ${workspaceFolder}/enum_pretty_printer.py",
            "ignoreFailures": false
        }
    ]
}
```

### Inheritance Testing

```json
{
    "name": "Debug Inheritance Test",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/examples/test_inheritance",
    "cwd": "${workspaceFolder}/examples",
    "MIMode": "gdb",
    "setupCommands": [
        {
            "description": "Enable pretty-printing",
            "text": "-enable-pretty-printing",
            "ignoreFailures": true
        },
        {
            "description": "Load inheritance test script",
            "text": "source test_inheritance.gdb",
            "ignoreFailures": false
        }
    ]
}
```

## Advanced Techniques

### 1. Conditional Script Loading

```json
{
    "description": "Load script if it exists",
    "text": "python import os; exec(open('optional_script.py').read()) if os.path.exists('optional_script.py') else None",
    "ignoreFailures": true
}
```

### 2. Setting Breakpoints in Scripts

```json
{
    "description": "Set breakpoint at specific location",
    "text": "break test_inheritance.cpp:52",
    "ignoreFailures": true
}
```

### 3. Environment-Specific Paths

```json
{
    "description": "Load formatter with environment variable",
    "text": "source $SYSTEMC_FORMATTER_PATH/sysc_gdb_formatter.py",
    "ignoreFailures": true
}
```

## Error Handling

### 1. Graceful Failure

Set `ignoreFailures: true` for optional scripts:

```json
{
    "description": "Load optional enhancement script",
    "text": "source optional_enhancements.gdb",
    "ignoreFailures": true
}
```

### 2. Required Scripts

Set `ignoreFailures: false` for essential scripts:

```json
{
    "description": "Load required formatter",
    "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
    "ignoreFailures": false
}
```

### 3. Debug Script Loading Issues

Add a test command to verify script loading:

```json
{
    "description": "Test if commands are available",
    "text": "python print('GDB Python scripting is working')",
    "ignoreFailures": true
}
```

## VS Code Integration Features

### 1. Variable Substitution

VS Code provides these variables:

- `${workspaceFolder}` - Root folder path
- `${file}` - Current file path
- `${fileBasename}` - Current filename
- `${fileDirname}` - Current file directory
- `${cwd}` - Current working directory

### 2. Multiple Configurations

Create different configurations for different scenarios:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug SystemC (GDB)",
            // SystemC-specific setup
        },
        {
            "name": "Debug Inheritance Test (GDB)",
            // Inheritance testing setup
        },
        {
            "name": "Debug with All Scripts (GDB)",
            // Load everything
        }
    ]
}
```

### 3. Build Task Integration

Link to build tasks with `preLaunchTask`:

```json
{
    "name": "Debug Inheritance Test",
    "preLaunchTask": "build-inheritance-test",
    // ... rest of configuration
}
```

## Complete Example

Here's our complete `launch.json` with GDB script loading:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug SystemC Example (GDB)",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/examples/test_example",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/examples",
            "MIMode": "gdb",
            "miDebuggerPath": "/usr/bin/gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                },
                {
                    "description": "Load SystemC GDB formatter",
                    "text": "source ${workspaceFolder}/sysc_gdb_formatter.py",
                    "ignoreFailures": false
                },
                {
                    "description": "Load enum pretty printer",
                    "text": "source ${workspaceFolder}/enum_pretty_printer.py",
                    "ignoreFailures": false
                }
            ],
            "preLaunchTask": "Build SystemC Example"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **Script not found**: Check file paths and use absolute paths or proper VS Code variables
2. **Python import errors**: Ensure GDB has Python support and required modules are available
3. **Permission errors**: Check file permissions for script files
4. **Syntax errors**: Validate your GDB scripts work independently first

### Debugging Script Loading

Add debug commands to verify loading:

```json
{
    "description": "Show loaded Python modules",
    "text": "python import sys; print('\\n'.join(sys.modules.keys()))",
    "ignoreFailures": true
}
```

### Testing Scripts Manually

Before adding to launch.json, test scripts manually:

```bash
gdb ./your_program
(gdb) source your_script.gdb
(gdb) run
```

## Best Practices

1. **Use descriptive names** for configurations
2. **Set appropriate `ignoreFailures`** values
3. **Test scripts independently** before integrating
4. **Use workspace-relative paths** when possible
5. **Group related configurations** logically
6. **Document complex setups** in comments

This configuration allows you to seamlessly debug with custom GDB scripts directly from VS Code, with automatic loading of formatters, pretty-printers, and debugging utilities.
