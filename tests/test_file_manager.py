import os
from nexum.core.file_manager import read_file, write_file, patch
from core.sovereign_execution_gateway import verify_audit_log

def test_file_system_engine():
    try:
        # Test write
        test_path = "test_file.txt"
        write_file(test_path, "Hello Nexum")
        assert read_file(test_path) == "Hello Nexum"
        
        # Test patch
        patch(test_path, "Hello", "Greetings")
        assert read_file(test_path) == "Greetings Nexum"
        
        # Test path traversal protection
        try:
            read_file("/etc/passwd")
            assert False, "Should have failed to read /etc/passwd"
        except PermissionError:
            print("Successfully blocked path traversal")
            
        # Verify integrity
        if verify_audit_log():
            print("Audit log integrity verified.")
        else:
            print("Audit log integrity check failed.")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_file_system_engine()
