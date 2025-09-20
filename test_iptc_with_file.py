import os
from iptcinfo3 import IPTCInfo

# Create a simple test with an actual JPG file
def test_iptc_with_jpg():
    # First, let's see what files are in the current directory
    files = os.listdir('.')
    jpg_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]
    
    if jpg_files:
        test_image = jpg_files[0]
        print(f"Found JPG file: {test_image}")
        
        try:
            # Create IPTCInfo object
            info = IPTCInfo(test_image)
            print("IPTCInfo created successfully")
            
            # Set some basic IPTC data
            info['object_name'] = 'Test Title'
            info['caption/abstract'] = 'Test Description'
            info['keywords'] = ['test', 'keyword']
            
            # Save the changes
            info.save()
            print("IPTC data saved successfully")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No JPG files found in current directory")
        # Create a simple test without an actual file
        try:
            print("Testing IPTCInfo creation with force=True")
            # This might not work as expected based on the documentation
            info = IPTCInfo(None, force=True)
            print("IPTCInfo created successfully")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_iptc_with_jpg()
