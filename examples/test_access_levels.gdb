# GDB script to test field access level detection
# Usage: gdb -x test_access_levels.gdb ./test_access_levels

echo === GDB Field Access Level Testing ===\n

# Compile and load the test program
shell g++ -g -o test_access_levels test_access_levels.cpp

# Load the program
file test_access_levels

# Source our access level analysis tools
python
import gdb

def analyze_field_access_levels(var_name):
    """Analyze access levels of all fields in a class/struct"""
    try:
        val = gdb.parse_and_eval(var_name)
        val_type = val.type
        
        print(f"\n=== Access Level Analysis: {var_name} ===")
        print(f"Type: {val_type}")
        
        # Get access level string
        def get_access_string(field):
            if hasattr(field, 'accessibility'):
                access = field.accessibility
                if access == gdb.FIELD_ACCESS_UNDEFINED:
                    return "undefined"
                elif access == gdb.FIELD_ACCESS_PUBLIC:
                    return "public"
                elif access == gdb.FIELD_ACCESS_PROTECTED:
                    return "protected"
                elif access == gdb.FIELD_ACCESS_PRIVATE:
                    return "private"
                else:
                    return f"unknown({access})"
            else:
                return "no_access_info"
        
        # Analyze all fields
        public_fields = []
        protected_fields = []
        private_fields = []
        base_classes = []
        other_fields = []
        
        for field in val_type.fields():
            access_level = get_access_string(field)
            field_info = {
                'name': field.name,
                'type': field.type,
                'access': access_level,
                'is_base': field.is_base_class,
                'artificial': field.artificial if hasattr(field, 'artificial') else False
            }
            
            if field.is_base_class:
                base_classes.append(field_info)
            elif access_level == "public":
                public_fields.append(field_info)
            elif access_level == "protected":
                protected_fields.append(field_info)
            elif access_level == "private":
                private_fields.append(field_info)
            else:
                other_fields.append(field_info)
        
        # Display results
        if base_classes:
            print("\nBase Classes:")
            for field in base_classes:
                print(f"  {field['access']} {field['type'].name}")
                if field['access'] in ['public', 'protected', 'private']:
                    print(f"    Access level: {field['access']}")
        
        if public_fields:
            print("\nPublic Members:")
            for field in public_fields:
                try:
                    value = val[field['name']]
                    print(f"  {field['name']}: {field['type']} = {value}")
                except gdb.error:
                    print(f"  {field['name']}: {field['type']} = <inaccessible>")
        
        if protected_fields:
            print("\nProtected Members:")
            for field in protected_fields:
                try:
                    value = val[field['name']]
                    print(f"  {field['name']}: {field['type']} = {value}")
                except gdb.error:
                    print(f"  {field['name']}: {field['type']} = <inaccessible>")
        
        if private_fields:
            print("\nPrivate Members:")
            for field in private_fields:
                try:
                    value = val[field['name']]
                    print(f"  {field['name']}: {field['type']} = {value}")
                except gdb.error:
                    print(f"  {field['name']}: {field['type']} = <inaccessible>")
        
        if other_fields:
            print("\nOther/Special Fields:")
            for field in other_fields:
                print(f"  {field['name']}: {field['type']} (access: {field['access']}, artificial: {field['artificial']})")
        
        # Summary
        print(f"\nSummary:")
        print(f"  Public fields: {len(public_fields)}")
        print(f"  Protected fields: {len(protected_fields)}")
        print(f"  Private fields: {len(private_fields)}")
        print(f"  Base classes: {len(base_classes)}")
        print(f"  Other fields: {len(other_fields)}")
        
    except gdb.error as e:
        print(f"Error analyzing {var_name}: {e}")

def check_field_accessibility_constants():
    """Check what accessibility constants are available"""
    print("\n=== GDB Field Accessibility Constants ===")
    
    constants = [
        ('FIELD_ACCESS_UNDEFINED', 'gdb.FIELD_ACCESS_UNDEFINED'),
        ('FIELD_ACCESS_PUBLIC', 'gdb.FIELD_ACCESS_PUBLIC'),
        ('FIELD_ACCESS_PROTECTED', 'gdb.FIELD_ACCESS_PROTECTED'),
        ('FIELD_ACCESS_PRIVATE', 'gdb.FIELD_ACCESS_PRIVATE'),
    ]
    
    for name, constant in constants:
        try:
            value = eval(constant)
            print(f"  {name}: {value}")
        except:
            print(f"  {name}: <not available>")

def filter_fields_by_access(var_name, access_level):
    """Get only fields with specific access level"""
    try:
        val = gdb.parse_and_eval(var_name)
        target_access = getattr(gdb, f'FIELD_ACCESS_{access_level.upper()}')
        
        matching_fields = []
        for field in val.type.fields():
            if hasattr(field, 'accessibility') and field.accessibility == target_access:
                matching_fields.append(field)
        
        print(f"\n{access_level.title()} fields in {var_name}:")
        for field in matching_fields:
            try:
                value = val[field.name]
                print(f"  {field.name}: {value}")
            except gdb.error:
                print(f"  {field.name}: <inaccessible>")
        
        return matching_fields
        
    except Exception as e:
        print(f"Error filtering fields: {e}")
        return []

def analyze_inheritance_access(var_name):
    """Analyze access levels in inheritance hierarchy"""
    try:
        val = gdb.parse_and_eval(var_name)
        
        print(f"\n=== Inheritance Access Analysis: {var_name} ===")
        
        for field in val.type.fields():
            if field.is_base_class:
                access_str = "public"
                if hasattr(field, 'accessibility'):
                    if field.accessibility == gdb.FIELD_ACCESS_PUBLIC:
                        access_str = "public"
                    elif field.accessibility == gdb.FIELD_ACCESS_PROTECTED:
                        access_str = "protected"
                    elif field.accessibility == gdb.FIELD_ACCESS_PRIVATE:
                        access_str = "private"
                
                print(f"Base class {field.type.name}: {access_str} inheritance")
                
                # Analyze base class members
                base_obj = val.cast(field.type)
                for base_field in field.type.fields():
                    if not base_field.is_base_class:
                        base_access = "unknown"
                        if hasattr(base_field, 'accessibility'):
                            if base_field.accessibility == gdb.FIELD_ACCESS_PUBLIC:
                                base_access = "public"
                            elif base_field.accessibility == gdb.FIELD_ACCESS_PROTECTED:
                                base_access = "protected"
                            elif base_field.accessibility == gdb.FIELD_ACCESS_PRIVATE:
                                base_access = "private"
                        
                        try:
                            member_val = base_obj[base_field.name]
                            print(f"  {base_access} {base_field.name}: {member_val}")
                        except gdb.error:
                            print(f"  {base_access} {base_field.name}: <inaccessible>")
    
    except Exception as e:
        print(f"Error analyzing inheritance access: {e}")

# Define GDB commands
class AnalyzeAccessCommand(gdb.Command):
    """Analyze field access levels of a variable"""
    
    def __init__(self):
        super().__init__("analyze-access", gdb.COMMAND_DATA)
    
    def invoke(self, arg, from_tty):
        if not arg:
            print("Usage: analyze-access <variable_name>")
            return
        analyze_field_access_levels(arg)

class FilterFieldsCommand(gdb.Command):
    """Filter fields by access level"""
    
    def __init__(self):
        super().__init__("filter-fields", gdb.COMMAND_DATA)
    
    def invoke(self, arg, from_tty):
        args = arg.split()
        if len(args) != 2:
            print("Usage: filter-fields <variable_name> <public|protected|private>")
            return
        filter_fields_by_access(args[0], args[1])

# Register commands
AnalyzeAccessCommand()
FilterFieldsCommand()

# Check available constants
check_field_accessibility_constants()

print("\nAccess level analysis tools loaded!")
print("Commands available:")
print("  analyze-access <var_name>               - Analyze all field access levels")
print("  filter-fields <var_name> <access_level> - Show only fields with specific access")
print("  python analyze_inheritance_access('var_name') - Analyze inheritance access levels")

end

# Set breakpoint and run
break test_access_levels.cpp:48
run

# Test access level analysis
echo \n=== Testing Simple Class ===\n
analyze-access test_obj

echo \n=== Testing Derived Class ===\n
analyze-access derived_obj

echo \n=== Testing Multiple Inheritance ===\n
analyze-access multi_obj

# Test filtering by access level
echo \n=== Testing Access Level Filtering ===\n
filter-fields test_obj public
filter-fields test_obj protected
filter-fields test_obj private

# Test inheritance access analysis
echo \n=== Testing Inheritance Access ===\n
python analyze_inheritance_access("derived_obj")
python analyze_inheritance_access("multi_obj")

echo \n=== Testing Complete ===\n
