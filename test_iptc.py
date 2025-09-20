from iptcinfo3 import IPTCInfo
import os

# Create a simple test
try:
    # Create a test image file if it doesn't exist
    test_image = "test.jpg"
    
    # If test.jpg doesn't exist, we'll just try to create an IPTCInfo object with force=True
    if not os.path.exists(test_image):
        print("Test image doesn't exist, creating IPTCInfo with force=True")
        info = IPTCInfo(force=True)
    else:
        info = IPTCInfo(test_image)
    
    print("IPTCInfo created successfully")
    
    # Set some basic IPTC data
    info['object_name'] = 'Test Title'
    info['caption/abstract'] = 'Test Description'
    info['keywords'] = ['test', 'keyword']
    
    print("IPTC data set successfully")
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
