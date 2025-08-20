# GDB script to test inheritance handling
# Usage: gdb -x test_inheritance.gdb ./test_inheritance

echo === GDB Inheritance Testing ===\n

# Compile and load the test program
shell g++ -g -o test_inheritance test_inheritance.cpp

# Load the program
file test_inheritance

# Source our inheritance helper
python
import gdb

def explore_inheritance(var_name):
    """Explore inheritance structure of a variable"""
    try:
        val = gdb.parse_and_eval(var_name)
        val_type = val.type
        
        print(f"\n=== Inheritance Analysis: {var_name} ===")
        print(f"Type: {val_type}")
        print(f"Size: {val_type.sizeof} bytes")
        
        # Check for base classes
        base_classes = []
        own_fields = []
        
        for field in val_type.fields():
            if field.is_base_class:
                base_classes.append(field)
                print(f"Base class: {field.type.name}")
                
                # Access base class members
                base_obj = val.cast(field.type)
                print(f"  Base object: {base_obj}")
                
                # Show base class fields
                for base_field in field.type.fields():
                    if not base_field.is_base_class:
                        try:
                            member_val = base_obj[base_field.name]
                            print(f"    {base_field.name}: {member_val}")
                        except gdb.error as e:
                            print(f"    {base_field.name}: <error: {e}>")
            else:
                own_fields.append(field)
        
        # Show own fields
        if own_fields:
            print("Own fields:")
            for field in own_fields:
                try:
                    member_val = val[field.name]
                    print(f"  {field.name}: {member_val}")
                except gdb.error as e:
                    print(f"  {field.name}: <error: {e}>")
        
        # Demonstrate casting
        if base_classes:
            print("\nCasting demonstrations:")
            for base_field in base_classes:
                print(f"Casting to {base_field.type.name}:")
                base_obj = val.cast(base_field.type)
                print(f"  Result: {base_obj}")
        
    except gdb.error as e:
        print(f"Error exploring {var_name}: {e}")

def access_member_through_inheritance(var_name, member_name):
    """Access a member that might be in base or derived class"""
    try:
        val = gdb.parse_and_eval(var_name)
        
        # Try direct access
        try:
            member = val[member_name]
            print(f"{var_name}.{member_name} = {member}")
            return member
        except gdb.error:
            pass
        
        # Try through base classes
        for field in val.type.fields():
            if field.is_base_class:
                try:
                    base_obj = val.cast(field.type)
                    member = base_obj[member_name]
                    print(f"{var_name}.{member_name} (via {field.type.name}) = {member}")
                    return member
                except gdb.error:
                    continue
        
        print(f"Member '{member_name}' not found in {var_name} or its base classes")
        return None
        
    except gdb.error as e:
        print(f"Error: {e}")
        return None

# Define a GDB command
class ExploreInheritanceCommand(gdb.Command):
    """Explore inheritance structure of a variable"""
    
    def __init__(self):
        super().__init__("explore-inheritance", gdb.COMMAND_DATA)
    
    def invoke(self, arg, from_tty):
        if not arg:
            print("Usage: explore-inheritance <variable_name>")
            return
        explore_inheritance(arg)

# Register the command
ExploreInheritanceCommand()

print("Inheritance exploration tools loaded!")
print("Commands available:")
print("  explore-inheritance <var_name>  - Analyze inheritance structure")
print("  python explore_inheritance('var_name')  - Python function")
print("  python access_member_through_inheritance('var_name', 'member_name')")

end

# Set breakpoint and run
break test_inheritance.cpp:52
run

# Now test our inheritance exploration
echo \n=== Testing Base Object ===\n
explore-inheritance base_obj

echo \n=== Testing Derived Object ===\n
explore-inheritance derived_obj

echo \n=== Testing Multiple Inheritance ===\n
explore-inheritance multi_obj

# Test member access through inheritance
echo \n=== Testing Member Access ===\n
python access_member_through_inheritance("derived_obj", "base_value")
python access_member_through_inheritance("derived_obj", "derived_float")
python access_member_through_inheritance("multi_obj", "base_value")
python access_member_through_inheritance("multi_obj", "another_value")

# Show direct GDB commands for comparison
echo \n=== Direct GDB Commands ===\n
print derived_obj
print derived_obj.base_value
print (BaseStruct)derived_obj
print multi_obj
print (BaseStruct)multi_obj
print (AnotherBase)multi_obj

echo \n=== Testing Complete ===\n
