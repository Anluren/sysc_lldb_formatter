#include <iostream>

// Test class with different access levels
class AccessTestClass {
public:
    int public_member;
    char public_char;
    
    AccessTestClass(int val, char c) : public_member(val), public_char(c), 
                                      protected_member(val * 2), 
                                      private_member(val * 3) {}
    
    void print_info() {
        std::cout << "Public: " << public_member << ", Protected: " << protected_member 
                  << ", Private: " << private_member << std::endl;
    }

protected:
    float protected_member;
    bool protected_flag = true;

private:
    double private_member;
    int private_array[3] = {1, 2, 3};
};

// Inheritance with different access levels
class DerivedClass : public AccessTestClass {
public:
    int derived_public;
    
    DerivedClass(int val) : AccessTestClass(val, 'D'), derived_public(val + 100) {}

protected:
    char derived_protected = 'X';

private:
    float derived_private = 3.14f;
};

// Multiple inheritance with different access
class AnotherBase {
public:
    int another_public = 42;
protected:
    char another_protected = 'A';
private:
    double another_private = 2.71;
};

class MultiAccessDerived : public AccessTestClass, protected AnotherBase {
public:
    int multi_public;
    
    MultiAccessDerived(int val) : AccessTestClass(val, 'M'), multi_public(val + 200) {}

private:
    bool multi_private = false;
};

int main() {
    AccessTestClass test_obj(10, 'T');
    DerivedClass derived_obj(20);
    MultiAccessDerived multi_obj(30);
    
    test_obj.print_info();
    derived_obj.print_info();
    
    std::cout << "Set breakpoint here for access level testing" << std::endl;
    
    return 0;
}
