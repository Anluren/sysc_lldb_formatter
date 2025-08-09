#include <systemc.h>
#include <iostream>

/**
 * Example SystemC program to test LLDB formatters
 * 
 * This program creates various SystemC data types with different
 * bit widths to demonstrate the formatter capabilities.
 * 
 * Compile with:
 *   g++ -std=c++17 -g -I<systemc_include> -L<systemc_lib> \
 *       test_example.cpp -lsystemc -o test_example
 * 
 * Debug with LLDB:
 *   lldb test_example
 *   (lldb) command script import sysc_lldb_formatter
 *   (lldb) breakpoint set --name sc_main
 *   (lldb) run
 *   (lldb) frame variable
 */

int sc_main(int argc, char* argv[]) {
    // 8-bit types
    sc_uint<8> uint8_val(0x42);     // 66 decimal
    sc_int<8> int8_val(-42);        // -42 decimal
    
    // 16-bit types
    sc_uint<16> uint16_val(0x1234);  // 4660 decimal
    sc_int<16> int16_val(-1000);     // -1000 decimal
    
    // 32-bit types
    sc_uint<32> uint32_val(0xDEADBEEF);  // 3735928559 decimal
    sc_int<32> int32_val(-123456789);    // -123456789 decimal
    
    // Edge cases
    sc_uint<1> single_bit(1);       // 1-bit unsigned
    sc_int<1> single_bit_signed(0); // 1-bit signed
    
    sc_uint<7> odd_width(127);      // Odd bit width
    sc_int<15> another_odd(-16384); // Another odd width
    
    // Maximum values for different widths
    sc_uint<8> max_uint8(255);      // Maximum 8-bit unsigned
    sc_int<8> min_int8(-128);       // Minimum 8-bit signed
    sc_int<8> max_int8(127);        // Maximum 8-bit signed
    
    std::cout << "SystemC test values created." << std::endl;
    std::cout << "Set breakpoint here and examine variables with LLDB." << std::endl;
    
    // Display some values for verification
    std::cout << "uint8_val = " << uint8_val << std::endl;
    std::cout << "int8_val = " << int8_val << std::endl;
    std::cout << "uint16_val = " << uint16_val << std::endl;
    std::cout << "int16_val = " << int16_val << std::endl;
    
    return 0; // Set breakpoint here
}
