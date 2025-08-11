#include <systemc.h>
#include <iostream>

int main() {
    // Test various SystemC integer types
    sc_dt::sc_uint<8> uint8_val = 255;
    sc_dt::sc_uint<16> uint16_val = 65535;
    sc_dt::sc_uint<32> uint32_val = 4294967295U;
    
    sc_dt::sc_int<8> int8_val = -128;
    sc_dt::sc_int<16> int16_val = -32768;
    sc_dt::sc_int<32> int32_val = -2147483648;
    
    // Set some specific values for testing
    uint8_val = 42;
    uint16_val = 1337;
    uint32_val = 0xDEADBEEF;
    
    int8_val = -42;
    int16_val = -1337;
    int32_val = -12345;
    
    std::cout << "SystemC Test Program" << std::endl;
    std::cout << "uint8_val = " << uint8_val << std::endl;
    std::cout << "uint16_val = " << uint16_val << std::endl;
    std::cout << "uint32_val = " << uint32_val << std::endl;
    std::cout << "int8_val = " << int8_val << std::endl;
    std::cout << "int16_val = " << int16_val << std::endl;
    std::cout << "int32_val = " << int32_val << std::endl;
    
    return 0;  // Set breakpoint here for debugging
}