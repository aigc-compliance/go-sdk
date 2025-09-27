#!/usr/bin/env python3
"""
Simple test to verify the Python SDK corrections
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aigc_compliance'))

from aigc_compliance import ComplianceClient

def test_client_initialization():
    """Test that client can be initialized"""
    try:
        client = ComplianceClient(api_key="test_key")
        print("✅ Client initialization: PASS")
        return True
    except Exception as e:
        print(f"❌ Client initialization: FAIL - {e}")
        return False

def test_health_method_exists():
    """Test that health method exists and is callable"""
    try:
        client = ComplianceClient(api_key="test_key")
        # Just check if method exists, don't actually call it
        assert hasattr(client, 'health'), "health method not found"
        assert callable(getattr(client, 'health')), "health method not callable"
        print("✅ Health method exists: PASS")
        return True
    except Exception as e:
        print(f"❌ Health method exists: FAIL - {e}")
        return False

def test_download_file_method_exists():
    """Test that download_file method exists and is callable"""
    try:
        client = ComplianceClient(api_key="test_key")
        # Just check if method exists, don't actually call it
        assert hasattr(client, 'download_file'), "download_file method not found"
        assert callable(getattr(client, 'download_file')), "download_file method not callable"
        print("✅ Download file method exists: PASS")
        return True
    except Exception as e:
        print(f"❌ Download file method exists: FAIL - {e}")
        return False

def test_comply_method_parameters():
    """Test that comply method has correct parameters"""
    try:
        client = ComplianceClient(api_key="test_key")
        import inspect
        
        # Get method signature
        sig = inspect.signature(client.comply)
        params = list(sig.parameters.keys())
        
        # Check for correct parameter name (file_path not image_path)
        assert 'file_path' in params, "file_path parameter not found"
        assert 'image_path' not in params, "old image_path parameter still exists"
        
        # Check region parameter default
        region_param = sig.parameters.get('region')
        assert region_param is not None, "region parameter not found"
        assert region_param.default == "EU", f"region default should be 'EU', got '{region_param.default}'"
        
        print("✅ Comply method parameters: PASS")
        return True
    except Exception as e:
        print(f"❌ Comply method parameters: FAIL - {e}")
        return False

def test_region_validation():
    """Test region validation in comply method"""
    try:
        client = ComplianceClient(api_key="test_key")
        
        # This should raise an error due to invalid region
        try:
            client.comply(file_path="test.jpg", region="invalid")
            print("❌ Region validation: FAIL - Should have raised ValueError")
            return False
        except ValueError as e:
            if "Region must be either 'EU' or 'CN'" in str(e):
                print("✅ Region validation: PASS")
                return True
            else:
                print(f"❌ Region validation: FAIL - Wrong error message: {e}")
                return False
        except FileNotFoundError:
            # This is expected since we're using a fake file path
            # But we should have hit the region validation first
            print("❌ Region validation: FAIL - Region validation bypassed")
            return False
    except Exception as e:
        print(f"❌ Region validation: FAIL - {e}")
        return False

def test_base_url_correction():
    """Test that base URL has been corrected"""
    try:
        client = ComplianceClient(api_key="test_key")
        expected_url = "https://api.aigc-compliance.com"
        
        assert client.base_url == expected_url, f"Base URL should be '{expected_url}', got '{client.base_url}'"
        print("✅ Base URL correction: PASS")
        return True
    except Exception as e:
        print(f"❌ Base URL correction: FAIL - {e}")
        return False

def main():
    """Run all tests"""
    print("Running Python SDK verification tests...\n")
    
    tests = [
        test_client_initialization,
        test_health_method_exists,
        test_download_file_method_exists,
        test_comply_method_parameters,
        test_region_validation,
        test_base_url_correction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Python SDK corrections are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())