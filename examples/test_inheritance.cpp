#include <iostream>

// Base struct
template <typename T>
struct BaseStruct {
    int base_value;
    char base_char;
    
    BaseStruct(int val, char c) : base_value(val), base_char(c) {}
    
    virtual void print_info() {
        std::cout << "Base: value=" << base_value << ", char=" << base_char << std::endl;
    }
};

// Derived struct
struct DerivedStruct : public BaseStruct <DerivedStruct> {
    float derived_float;
    bool derived_flag;
    
    DerivedStruct(int val, char c, float f, bool flag) 
        : BaseStruct(val, c), derived_float(f), derived_flag(flag) {}
    
    void print_info() override {
        std::cout << "Derived: value=" << base_value << ", char=" << base_char 
                  << ", float=" << derived_float << ", flag=" << derived_flag << std::endl;
    }
};

// Multiple inheritance example
struct AnotherBase {
    double another_value;
    AnotherBase(double val) : another_value(val) {}
};

struct MultiDerived : public BaseStruct <MultiDerived>, public AnotherBase {
    int multi_int;
    
    MultiDerived(int base_val, char c, double another_val, int multi) 
        : BaseStruct(base_val, c), AnotherBase(another_val), multi_int(multi) {}
};

int main() {
    // Create test objects
    // BaseStruct base_obj(42, 'A');
    DerivedStruct derived_obj(100, 'B', 3.14f, true);
    MultiDerived multi_obj(200, 'C', 2.71, 999);
    
    // Print information
    std::cout << "=== Inheritance Test Objects ===" << std::endl;
    // base_obj.print_info();
    derived_obj.print_info();
    
    std::cout << "Multi inheritance object:" << std::endl;
    std::cout << "  BaseStruct part: value=" << multi_obj.base_value 
              << ", char=" << multi_obj.base_char << std::endl;
    std::cout << "  AnotherBase part: value=" << multi_obj.another_value << std::endl;
    std::cout << "  Own member: multi_int=" << multi_obj.multi_int << std::endl;
    
    // Set breakpoint here for GDB testing
    std::cout << "Set breakpoint here for GDB inheritance testing" << std::endl;
    
    return 0;
}
