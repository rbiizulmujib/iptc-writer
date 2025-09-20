from iptcinfo3 import IPTCInfo

# Test with a specific image
try:
    # Create IPTCInfo object
    info = IPTCInfo('icon_-01.jpg', force=True)
    
    # Set some test data
    info['object name'] = 'Test Title'
    info['caption/abstract'] = 'Test Description'
    info['keywords'] = ['test', 'keyword']
    
    # Save the changes
    info.save()
    print("IPTC data written successfully")
    
except Exception as e:
    print(f"Error: {e}")
