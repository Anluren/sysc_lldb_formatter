#!/usr/bin/env python3
"""
Example: Working with inheritance in GDB Python API

This demonstrates how to handle struct inheritance when working with gdb.Value objects.
"""

import gdb

class InheritancePrinter:
    """Pretty printer that handles inheritance relationships"""
    
    def __init__(self, val):
        self.val = val
        self.type = val.type
    
    def get_base_classes(self):
        """Get all base classes of the current type"""
        base_classes = []
        for field in self.type.fields():
            if field.is_base_class:
                base_classes.append({
                    'name': field.type.name,
                    'type': field.type,
                    'value': self.val.cast(field.type)
                })
        return base_classes
    
    def get_base_class_value(self, base_class_name):
        """Get the base class subobject by name"""
        for field in self.type.fields():
            if field.is_base_class and field.type.name == base_class_name:
                return self.val.cast(field.type)
        return None
    
    def access_member_in_hierarchy(self, member_name):
        """Access a member that might be in base class or derived class"""
        # Try direct access first
        try:
            return self.val[member_name]
        except gdb.error:
            pass
        
        # Search in base classes
        for field in self.type.fields():
            if field.is_base_class:
                try:
                    base_obj = self.val.cast(field.type)
                    return base_obj[member_name]
                except gdb.error:
                    continue
        
        raise gdb.error(f"Member '{member_name}' not found in class hierarchy")
    
    def to_string(self):
        """Pretty print showing inheritance hierarchy"""
        result = f"{self.type.name} {{"
        
        # Show base classes first
        base_classes = self.get_base_classes()
        if base_classes:
            result += "\n  Base classes:"
            for base in base_classes:
                result += f"\n    {base['name']}: {base['value']}"
        
        # Show own members
        result += "\n  Members:"
        for field in self.type.fields():
            if not field.is_base_class:
                try:
                    member_val = self.val[field.name]
                    result += f"\n    {field.name}: {member_val}"
                except:
                    result += f"\n    {field.name}: <unavailable>"
        
        result += "\n}"
        return result

def inheritance_demo():
    """Demonstrate inheritance handling techniques"""
    
    # Example usage in GDB commands
    print("=== Inheritance Handling Demo ===")
    
    # Get a value (this would typically come from gdb.parse_and_eval)
    try:
        derived_obj = gdb.parse_and_eval("some_derived_object")
        
        # Method 1: Direct member access (works across inheritance)
        print("1. Direct member access:")
        try:
            member = derived_obj["some_member"]
            print(f"   Member value: {member}")
        except gdb.error as e:
            print(f"   Error: {e}")
        
        # Method 2: Cast to base class
        print("2. Cast to base class:")
        try:
            base_type = gdb.lookup_type("BaseClass")
            base_obj = derived_obj.cast(base_type)
            print(f"   Base object: {base_obj}")
        except gdb.error as e:
            print(f"   Error: {e}")
        
        # Method 3: Use our helper class
        print("3. Using InheritancePrinter:")
        printer = InheritancePrinter(derived_obj)
        print(f"   {printer.to_string()}")
        
    except gdb.error as e:
        print(f"Demo requires a valid object in GDB context: {e}")

class InheritanceExplorerCommand(gdb.Command):
    """GDB command to explore inheritance relationships"""
    
    def __init__(self):
        super().__init__("explore-inheritance", gdb.COMMAND_DATA)
    
    def invoke(self, arg, from_tty):
        """Explore inheritance of a given variable or type"""
        if not arg:
            print("Usage: explore-inheritance <variable_name>")
            return
        
        try:
            val = gdb.parse_and_eval(arg)
            printer = InheritancePrinter(val)
            
            print(f"Inheritance analysis for '{arg}':")
            print(f"Type: {val.type}")
            
            base_classes = printer.get_base_classes()
            if base_classes:
                print("\nBase classes:")
                for i, base in enumerate(base_classes):
                    print(f"  {i+1}. {base['name']}")
                    print(f"     Type: {base['type']}")
                    
                    # Show base class members
                    try:
                        for field in base['type'].fields():
                            if not field.is_base_class:
                                member_val = base['value'][field.name]
                                print(f"     {field.name}: {member_val}")
                    except:
                        print("     <members not accessible>")
            else:
                print("\nNo base classes found.")
            
            print(f"\nPretty printed:")
            print(printer.to_string())
            
        except gdb.error as e:
            print(f"Error: {e}")

# Register the command
InheritanceExplorerCommand()

if __name__ == "__main__":
    inheritance_demo()
