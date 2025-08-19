#include <iostream>

// Example enum types for testing enum pretty-printing
enum class Color {
    RED = 0,
    GREEN = 1,
    BLUE = 2,
    YELLOW = 3
};

enum State {
    STATE_IDLE = 0,
    STATE_PROCESSING = 10,
    STATE_ERROR = 20,
    STATE_SHUTDOWN = 30
};

// SystemC-style enum (if you have SystemC available)
// #include <systemc.h>
// using namespace sc_core;
// using namespace sc_dt;

int main() {
    // Test different enum types
    Color my_color = Color::RED;
    State my_state = STATE_PROCESSING;
    
    // SystemC enums (uncomment if SystemC is available)
    // sc_logic_value_t logic_val = SC_LOGIC_1;
    // sc_time_unit time_unit = SC_NS;
    
    std::cout << "Enum test program" << std::endl;
    std::cout << "Set breakpoint here to test enum formatting" << std::endl;
    
    // Change some values for testing
    my_color = Color::BLUE;
    my_state = STATE_ERROR;
    
    return 0;  // Set breakpoint here
}
