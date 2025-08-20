# Field Access Level Detection in GDB Python API

This document explains how to determine if a `gdb.Field` is public, protected, or private in GDB's Python API.

## Current Status of Field Accessibility

### GDB Version Support

**The `accessibility` attribute for `gdb.Field` is not widely supported** in most GDB versions. Our testing shows:

- **GDB 12.1 (Ubuntu 22.04)**: ❌ No `accessibility` attribute
- **Older GDB versions**: ❌ Generally not supported
- **Recent GDB versions**: ❓ May have limited support

### Expected API (If Supported)

If your GDB version supports field accessibility, the API would look like:

```python
import gdb

# Access level constants (if available)
gdb.FIELD_ACCESS_UNDEFINED  # 0
gdb.FIELD_ACCESS_PUBLIC     # 1  
gdb.FIELD_ACCESS_PROTECTED  # 2
gdb.FIELD_ACCESS_PRIVATE    # 3

# Usage
def get_field_access_level(field):
    """Get access level of a field (if supported)"""
    if hasattr(field, 'accessibility'):
        access = field.accessibility
        if access == gdb.FIELD_ACCESS_PUBLIC:
            return "public"
        elif access == gdb.FIELD_ACCESS_PROTECTED:
            return "protected"
        elif access == gdb.FIELD_ACCESS_PRIVATE:
            return "private"
        else:
            return "undefined"
    return "unsupported"
```

## Alternative Detection Methods

Since direct access level detection is not widely supported, here are practical alternatives:

### 1. Name-Based Heuristics

```python
def guess_access_from_name(field_name):
    """Guess access level from field naming conventions"""
    name_lower = field_name.lower()
    
    # Common naming patterns
    if name_lower.startswith('m_'):
        return "private"  # Member variable prefix
    elif name_lower.startswith('_'):
        return "private"  # Leading underscore
    elif 'private' in name_lower:
        return "private"
    elif 'protected' in name_lower:
        return "protected"
    elif 'public' in name_lower:
        return "public"
    else:
        return "unknown"

# Example usage
for field in my_type.fields():
    if not field.is_base_class:
        guessed_access = guess_access_from_name(field.name)
        print(f"{field.name}: likely {guessed_access}")
```

### 2. Debug Info Analysis

```python
def analyze_debug_info_access(type_obj):
    """Analyze debug information for access clues"""
    
    # Check if debug info contains access information
    # This is GDB version and compiler dependent
    try:
        # Some debug formats may include access information in type names
        type_str = str(type_obj)
        if 'public:' in type_str or 'protected:' in type_str or 'private:' in type_str:
            print("Debug info may contain access level information")
            return True
    except:
        pass
    
    return False
```

### 3. Runtime Access Testing

```python
def test_field_accessibility(obj_value, field_name):
    """Test if a field is accessible at runtime"""
    try:
        # Try to access the field
        value = obj_value[field_name]
        return "accessible"
    except gdb.error as e:
        error_msg = str(e).lower()
        if 'private' in error_msg or 'protected' in error_msg:
            return "restricted"
        elif 'no such' in error_msg:
            return "not_found"
        else:
            return "error"
```

### 4. Source Code Parsing (Advanced)

```python
def parse_source_for_access_levels(source_file, class_name):
    """Parse C++ source code to determine access levels"""
    try:
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Simple parser for access sections
        import re
        
        # Find class definition
        class_pattern = rf'class\s+{class_name}\s*[{{:]'
        class_match = re.search(class_pattern, content)
        
        if class_match:
            # Extract class body and parse access sections
            # This is a simplified example - real parsing would be more complex
            access_sections = {
                'public': [],
                'protected': [], 
                'private': []
            }
            
            # Find access level keywords and following members
            access_pattern = r'(public|protected|private)\s*:'
            
            # Note: This is a very basic parser
            # For production use, consider using a proper C++ parser
            
            return access_sections
    
    except Exception as e:
        print(f"Source parsing error: {e}")
    
    return None
```

## Practical Implementation

Here's a complete practical implementation that combines multiple approaches:

```python
class FieldAccessAnalyzer:
    """Comprehensive field access level analyzer"""
    
    def __init__(self):
        self.has_accessibility = self._check_accessibility_support()
    
    def _check_accessibility_support(self):
        """Check if this GDB version supports field accessibility"""
        try:
            # Try to find accessibility constants
            return hasattr(gdb, 'FIELD_ACCESS_PUBLIC')
        except:
            return False
    
    def get_access_level(self, field, context=None):
        """Get access level using best available method"""
        
        # Method 1: Direct accessibility attribute (if supported)
        if self.has_accessibility and hasattr(field, 'accessibility'):
            return self._map_accessibility_constant(field.accessibility)
        
        # Method 2: Name-based heuristics
        name_guess = self._guess_from_name(field.name)
        if name_guess != "unknown":
            return f"{name_guess}_guessed"
        
        # Method 3: Context-based analysis
        if context:
            context_guess = self._analyze_context(field, context)
            if context_guess:
                return context_guess
        
        return "unknown"
    
    def _map_accessibility_constant(self, accessibility):
        """Map accessibility constant to string"""
        access_map = {
            0: "undefined",
            1: "public",
            2: "protected", 
            3: "private"
        }
        return access_map.get(accessibility, "unknown")
    
    def _guess_from_name(self, name):
        """Guess access from naming conventions"""
        if not name:
            return "unknown"
        
        name_lower = name.lower()
        
        # Common patterns
        if name_lower.startswith('m_'):
            return "private"
        elif name_lower.startswith('_'):
            return "private"
        elif name.startswith('__'):
            return "private"
        elif 'private' in name_lower:
            return "private"
        elif 'protected' in name_lower:
            return "protected"
        elif 'public' in name_lower:
            return "public"
        
        return "unknown"
    
    def _analyze_context(self, field, context):
        """Analyze field in context for access clues"""
        # Could include position analysis, pattern matching, etc.
        return None
    
    def analyze_all_fields(self, type_obj, obj_value=None):
        """Analyze access levels of all fields in a type"""
        results = {
            'public': [],
            'protected': [],
            'private': [],
            'unknown': []
        }
        
        for field in type_obj.fields():
            if not field.is_base_class:
                access_level = self.get_access_level(field, obj_value)
                
                # Clean up guessed results
                clean_access = access_level.replace('_guessed', '')
                if clean_access in results:
                    results[clean_access].append({
                        'name': field.name,
                        'type': field.type,
                        'access': access_level,
                        'confidence': 'high' if '_guessed' not in access_level else 'low'
                    })
                else:
                    results['unknown'].append({
                        'name': field.name,
                        'type': field.type,
                        'access': access_level,
                        'confidence': 'none'
                    })
        
        return results

# Usage example
def demo_access_analysis():
    """Demonstrate access level analysis"""
    analyzer = FieldAccessAnalyzer()
    
    try:
        # Analyze a type
        test_type = gdb.lookup_type("AccessTestClass")
        results = analyzer.analyze_all_fields(test_type)
        
        print("Access Level Analysis Results:")
        for access_level, fields in results.items():
            if fields:
                print(f"\n{access_level.title()} fields:")
                for field_info in fields:
                    print(f"  {field_info['name']}: {field_info['type']} "
                          f"(confidence: {field_info['confidence']})")
    
    except Exception as e:
        print(f"Analysis error: {e}")
```

## Recommendations

### For SystemC Pretty Printers

When working with SystemC types in pretty printers:

1. **Use naming conventions**: SystemC often follows clear naming patterns
2. **Focus on accessible members**: Usually only need public members for display
3. **Document assumptions**: Note when access level detection is heuristic-based
4. **Provide fallbacks**: Handle cases where access detection fails

```python
def format_systemc_object(value):
    """Format SystemC object considering access levels"""
    analyzer = FieldAccessAnalyzer()
    
    # Get public fields for display
    all_fields = analyzer.analyze_all_fields(value.type, value)
    public_fields = all_fields.get('public', [])
    
    # Format for display
    result = f"{value.type.name} {{"
    for field_info in public_fields:
        try:
            member_value = value[field_info['name']]
            result += f"\n  {field_info['name']}: {member_value}"
        except:
            result += f"\n  {field_info['name']}: <inaccessible>"
    
    result += "\n}"
    return result
```

## Future GDB Versions

Keep an eye on future GDB releases that may add better support for field accessibility. When available, update your code to use the direct `accessibility` attribute for more reliable access level detection.

## Testing

Use the provided test files to check accessibility support in your GDB version:

- `test_access_levels.cpp` - C++ test program with different access levels
- `simple_access_test.gdb` - GDB script to test accessibility support
- Run: `gdb -x simple_access_test.gdb ./test_access_levels`

This will show you what accessibility features are available in your specific GDB installation.
