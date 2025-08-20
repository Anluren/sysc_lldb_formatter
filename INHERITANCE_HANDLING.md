# Working with Inheritance in GDB Python API

This document explains how to handle struct/class inheritance when working with `gdb.Value` objects in GDB's Python API.

## Overview

When dealing with inheritance in C++, GDB's Python API provides several mechanisms to access base class members and handle inheritance relationships through `gdb.Value` objects.

## Key Concepts

### 1. Base Class Detection

GDB automatically detects inheritance relationships. You can identify base classes by checking the `is_base_class` property of type fields:

```python
def get_base_classes(value):
    """Get all base classes of a value"""
    base_classes = []
    for field in value.type.fields():
        if field.is_base_class:
            base_classes.append({
                'name': field.type.name,
                'type': field.type,
                'value': value.cast(field.type)
            })
    return base_classes
```

### 2. Member Access Across Inheritance

GDB allows direct access to base class members from derived objects:

```python
# Direct access - works for both derived and base class members
derived_value = gdb.parse_and_eval("derived_obj")
base_member = derived_value["base_member_name"]  # Accesses base class member
derived_member = derived_value["derived_member_name"]  # Accesses derived class member
```

### 3. Casting to Base Types

You can cast a derived object to its base type to access it as the base class:

```python
def cast_to_base(value, base_class_name):
    """Cast a derived object to its base class"""
    try:
        base_type = gdb.lookup_type(base_class_name)
        return value.cast(base_type)
    except gdb.error as e:
        print(f"Cannot cast to {base_class_name}: {e}")
        return None

# Usage
derived_obj = gdb.parse_and_eval("my_derived_obj")
base_obj = cast_to_base(derived_obj, "BaseClass")
```

## Practical Examples

### Example 1: Simple Inheritance

```cpp
struct Base {
    int base_value;
    char base_char;
};

struct Derived : public Base {
    float derived_float;
    bool derived_flag;
};
```

**GDB Python handling:**

```python
def analyze_simple_inheritance(var_name):
    val = gdb.parse_and_eval(var_name)
    
    # Access base members directly
    base_value = val["base_value"]
    base_char = val["base_char"]
    
    # Access derived members
    derived_float = val["derived_float"]
    derived_flag = val["derived_flag"]
    
    # Cast to base type
    base_obj = val.cast(gdb.lookup_type("Base"))
    
    print(f"Base part: {base_obj}")
    print(f"Full object: {val}")
```

### Example 2: Multiple Inheritance

```cpp
struct BaseA {
    int a_value;
};

struct BaseB {
    double b_value;
};

struct MultiDerived : public BaseA, public BaseB {
    char multi_char;
};
```

**GDB Python handling:**

```python
def analyze_multiple_inheritance(var_name):
    val = gdb.parse_and_eval(var_name)
    
    # Find all base classes
    for field in val.type.fields():
        if field.is_base_class:
            base_obj = val.cast(field.type)
            print(f"Base class {field.type.name}: {base_obj}")
            
            # Access base class members
            for base_field in field.type.fields():
                if not base_field.is_base_class:
                    member_val = base_obj[base_field.name]
                    print(f"  {base_field.name}: {member_val}")
```

## Advanced Techniques

### 1. Hierarchical Member Search

```python
def find_member_in_hierarchy(value, member_name):
    """Search for a member in the entire inheritance hierarchy"""
    
    # Try direct access first
    try:
        return value[member_name]
    except gdb.error:
        pass
    
    # Search in base classes recursively
    def search_in_type(val, val_type):
        for field in val_type.fields():
            if field.is_base_class:
                base_obj = val.cast(field.type)
                try:
                    return base_obj[member_name]
                except gdb.error:
                    # Recursive search
                    result = search_in_type(base_obj, field.type)
                    if result is not None:
                        return result
        return None
    
    return search_in_type(value, value.type)
```

### 2. Type Relationship Checking

```python
def is_derived_from(derived_type, base_class_name):
    """Check if a type is derived from a specific base class"""
    if derived_type.name == base_class_name:
        return True
    
    for field in derived_type.fields():
        if field.is_base_class:
            if field.type.name == base_class_name:
                return True
            # Recursive check for indirect inheritance
            if is_derived_from(field.type, base_class_name):
                return True
    return False
```

### 3. Complete Inheritance Pretty Printer

```python
class InheritancePrettyPrinter:
    """Pretty printer that shows inheritance hierarchy"""
    
    def __init__(self, val):
        self.val = val
        self.type = val.type
    
    def get_inheritance_chain(self):
        """Get the complete inheritance chain"""
        chain = [self.type.name]
        
        def collect_bases(val_type):
            for field in val_type.fields():
                if field.is_base_class:
                    chain.append(field.type.name)
                    collect_bases(field.type)
        
        collect_bases(self.type)
        return chain
    
    def to_string(self):
        result = f"{self.type.name}"
        
        # Show inheritance chain
        chain = self.get_inheritance_chain()
        if len(chain) > 1:
            result += f" (inherits from: {' -> '.join(reversed(chain[1:]))})"
        
        result += " {\n"
        
        # Show base classes with their members
        for field in self.type.fields():
            if field.is_base_class:
                base_obj = self.val.cast(field.type)
                result += f"  [{field.type.name}] {base_obj}\n"
        
        # Show own members
        result += "  Own members:\n"
        for field in self.type.fields():
            if not field.is_base_class:
                try:
                    member_val = self.val[field.name]
                    result += f"    {field.name}: {member_val}\n"
                except gdb.error:
                    result += f"    {field.name}: <unavailable>\n"
        
        result += "}"
        return result
```

## Memory Layout Considerations

When working with inheritance, be aware of memory layout:

1. **Virtual Functions**: Classes with virtual functions have a vtable pointer
2. **Multiple Inheritance**: Base classes are laid out sequentially in memory
3. **Virtual Inheritance**: Has different memory layout (virtual base table)
4. **Padding**: Compiler may add padding between base and derived parts

### Memory Offset Access

```python
def get_base_at_offset(value, base_type_name, offset=0):
    """Access base class at specific memory offset"""
    try:
        base_type = gdb.lookup_type(base_type_name)
        base_addr = value.address + offset
        return base_addr.cast(base_type.pointer()).dereference()
    except gdb.error as e:
        print(f"Error accessing base at offset {offset}: {e}")
        return None
```

## Common Patterns

### 1. SystemC-style Inheritance

Many SystemC classes inherit from base classes that provide common functionality:

```python
def handle_systemc_inheritance(sc_object):
    """Handle SystemC object inheritance patterns"""
    
    # Check if it's a SystemC object
    if is_derived_from(sc_object.type, "sc_object"):
        base_obj = sc_object.cast(gdb.lookup_type("sc_object"))
        name = base_obj["m_name"]  # Access base class member
        return f"SystemC object: {name}"
    
    return "Not a SystemC object"
```

### 2. Generic Inheritance Handler

```python
def create_inheritance_handler(base_class_handlers):
    """Create a generic inheritance handler"""
    
    def handle_object(value):
        for base_name, handler in base_class_handlers.items():
            if is_derived_from(value.type, base_name):
                return handler(value)
        return f"Unknown object type: {value.type.name}"
    
    return handle_object

# Usage
handlers = {
    "BaseStruct": lambda val: f"BaseStruct with value: {val['base_value']}",
    "sc_object": lambda val: f"SystemC object: {val.cast(gdb.lookup_type('sc_object'))['m_name']}",
}

inheritance_handler = create_inheritance_handler(handlers)
```

## Best Practices

1. **Always check for `gdb.error`** when accessing members or casting
2. **Use `is_base_class`** to identify inheritance relationships
3. **Cast explicitly** when you need to access an object as its base type
4. **Handle virtual inheritance** carefully - it has different memory layout
5. **Consider vtable pointers** when dealing with polymorphic classes
6. **Use recursive search** for deep inheritance hierarchies

## GDB Commands

The examples include a custom GDB command `explore-inheritance` that you can use interactively:

```gdb
(gdb) explore-inheritance my_derived_object
```

This command will show:
- All base classes
- Members in each base class
- Casting demonstrations
- Memory layout information

## Testing

Use the provided test files:
- `test_inheritance.cpp` - C++ program with various inheritance patterns
- `test_inheritance.gdb` - GDB script to test inheritance handling
- `inheritance_example.py` - Python module with inheritance utilities

Run the test:
```bash
gdb -x test_inheritance.gdb ./test_inheritance
```

This comprehensive approach allows you to handle any inheritance scenario you might encounter when working with `gdb.Value` objects in SystemC or other C++ codebases.
