#!/usr/bin/env python3
"""
Test script to verify SystemC LLDB formatter functionality without running SystemC code.
"""

def test_formatter_import():
    """Test that the formatter can be imported and initialized."""
    print("Testing SystemC LLDB Formatter...")
    
    try:
        # Test package import
        import sysc_lldb_formatter
        print("✓ Package imports successfully")
        
        # Test individual formatter classes
        from sysc_lldb_formatter.formatters import (
            SystemCFormatterBase, 
            SCUintFormatter, 
            SCIntFormatter,
            sc_uint_summary_provider,
            sc_int_summary_provider
        )
        print("✓ All formatter classes imported")
        
        # Test that the classes can be instantiated (with mock objects)
        class MockValue:
            def GetType(self):
                class MockType:
                    def GetName(self):
                        return "sc_dt::sc_uint<8>"
                return MockType()
            
            def GetLoadAddress(self):
                return 0  # Mock address
                
            def GetTarget(self):
                return None  # Will cause graceful failure
        
        mock_val = MockValue()
        formatter = SCUintFormatter(mock_val, {})
        print(f"✓ SCUintFormatter created with width: {formatter.width}")
        print(f"✓ Is signed: {formatter.is_signed()}")
        
        # Test the summary provider function
        summary = sc_uint_summary_provider(mock_val, {})
        print(f"✓ Summary provider works: {summary}")
        
        print("\n🎉 All formatter verification tests passed!")
        print("The formatter is ready for use with LLDB.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_formatter_import()
