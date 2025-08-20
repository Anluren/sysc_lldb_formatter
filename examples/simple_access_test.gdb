# Simple GDB test for field accessibility
# Usage: gdb -x simple_access_test.gdb ./test_access_levels

echo === Simple Field Access Test ===\n

file test_access_levels

python
import gdb

# Test if accessibility attribute exists
def test_field_accessibility():
    """Test field accessibility detection"""
    print("Testing field accessibility support...")
    
    # Try to get type information
    try:
        # Get type without running program
        test_type = gdb.lookup_type("AccessTestClass")
        print(f"Found type: {test_type}")
        
        print("\nFields and their properties:")
        for field in test_type.fields():
            print(f"Field: {field.name}")
            print(f"  Type: {field.type}")
            print(f"  Is base class: {field.is_base_class}")
            
            # Check for accessibility attribute
            if hasattr(field, 'accessibility'):
                print(f"  Accessibility attribute: {field.accessibility}")
                
                # Try to map to constants
                access_map = {
                    0: "undefined/unknown",
                    1: "public", 
                    2: "protected",
                    3: "private"
                }
                access_str = access_map.get(field.accessibility, f"unknown_value_{field.accessibility}")
                print(f"  Access level: {access_str}")
            else:
                print("  No accessibility attribute")
            
            # Check for other attributes
            attrs = ['artificial', 'bitpos', 'bitsize']
            for attr in attrs:
                if hasattr(field, attr):
                    print(f"  {attr}: {getattr(field, attr)}")
            
            print()
    
    except Exception as e:
        print(f"Error: {e}")

def check_gdb_constants():
    """Check what GDB constants are available"""
    print("Checking GDB constants...")
    
    # List of possible constants to check
    possible_constants = [
        'FIELD_ACCESS_UNDEFINED',
        'FIELD_ACCESS_PUBLIC', 
        'FIELD_ACCESS_PROTECTED',
        'FIELD_ACCESS_PRIVATE',
        # Alternative naming
        'FIELD_PUBLIC',
        'FIELD_PROTECTED', 
        'FIELD_PRIVATE',
    ]
    
    available_constants = []
    
    for const_name in possible_constants:
        try:
            value = getattr(gdb, const_name, None)
            if value is not None:
                available_constants.append((const_name, value))
                print(f"  {const_name}: {value}")
        except:
            pass
    
    if not available_constants:
        print("  No field access constants found in gdb module")
        print("  This GDB version may not support field accessibility")
    
    return available_constants

def alternative_access_detection():
    """Alternative method to detect access levels"""
    print("\nAlternative access level detection methods:")
    
    try:
        test_type = gdb.lookup_type("AccessTestClass")
        
        # Method 1: Field name patterns (heuristic)
        print("Method 1: Name-based heuristics")
        for field in test_type.fields():
            if not field.is_base_class:
                name = field.name
                if 'public' in name:
                    print(f"  {name}: likely public (name contains 'public')")
                elif 'protected' in name:
                    print(f"  {name}: likely protected (name contains 'protected')")
                elif 'private' in name:
                    print(f"  {name}: likely private (name contains 'private')")
                else:
                    print(f"  {name}: unknown access level")
        
        # Method 2: Try to access from derived class context
        print("\nMethod 2: Access testing (requires running program)")
        print("  This would require setting up object instances and testing access")
        
    except Exception as e:
        print(f"Error in alternative detection: {e}")

# Run tests
test_field_accessibility()
check_gdb_constants()
alternative_access_detection()

end

# Set a breakpoint in main and run briefly
break main
run
continue

# Test with actual objects
python
try:
    # Try to analyze the type again with program running
    print("\n=== With Program Running ===")
    
    # Look for local variables
    frame = gdb.selected_frame()
    block = frame.block()
    
    print("Local variables in current frame:")
    for symbol in block:
        if symbol.is_variable:
            print(f"  {symbol.name}: {symbol.type}")
    
    # Try to get the type information again
    test_type = gdb.lookup_type("AccessTestClass")
    print(f"\nRe-analyzing {test_type}:")
    
    for field in test_type.fields():
        if not field.is_base_class:
            print(f"  {field.name}:")
            
            # Check all available attributes
            attrs = dir(field)
            relevant_attrs = [attr for attr in attrs if not attr.startswith('_')]
            print(f"    Available attributes: {relevant_attrs}")
            
            # Try to get accessibility if available
            if 'accessibility' in attrs:
                print(f"    accessibility: {field.accessibility}")

except Exception as e:
    print(f"Error with running program: {e}")
end

echo \n=== Simple Test Complete ===\n
