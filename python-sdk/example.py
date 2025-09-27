#!/usr/bin/env python3
"""
AIGC Compliance Python SDK - Example Usage

This example demonstrates how to use the AIGC Compliance Python SDK
to make AI-generated images compliant with regional regulations.
"""

import os
from aigc_compliance import ComplianceClient

def main():
    # Initialize client with API key from environment
    api_key = os.getenv("AIGC_API_KEY")
    if not api_key:
        print("Error: AIGC_API_KEY environment variable is required")
        return
    
    client = ComplianceClient(api_key=api_key)
    
    try:
        # Check API health
        print("Checking API health...")
        health_status = client.health()
        print(f"API Status: {health_status}")
        
        # Example 1: Basic compliance check for EU region
        print("\n=== Basic Compliance Check (EU) ===")
        image_path = "test_image.jpg"  # Replace with actual image path
        
        if os.path.exists(image_path):
            result = client.comply(
                file_path=image_path,
                region="EU",
                watermark_position="bottom-right",
                include_base64=True,
                save_to_disk=False
            )
            
            print(f"Compliance Result: {result.get('compliant', False)}")
            print(f"AI Detection Score: {result.get('ai_probability', 'N/A')}")
            print(f"Processing Time: {result.get('processing_time', 'N/A')}ms")
            
            # Save processed image if included in response
            if result.get('processedImage') and result['processedImage'].startswith('data:'):
                import base64
                image_data = result['processedImage'].split(',')[1]
                with open('processed_image.jpg', 'wb') as f:
                    f.write(base64.b64decode(image_data))
                print("Processed image saved as 'processed_image.jpg'")
        else:
            print(f"Image file not found: {image_path}")
        
        # Example 2: Compliance check for China region with custom logo
        print("\n=== Compliance Check with Custom Logo (CN) ===")
        logo_path = "custom_logo.png"  # Replace with actual logo path
        
        if os.path.exists(image_path) and os.path.exists(logo_path):
            result = client.comply(
                file_path=image_path,
                region="CN",
                watermark_position="top-left",
                logo_file=logo_path,
                include_base64=False,
                save_to_disk=True,
                output_path="cn_compliant_image.jpg"
            )
            
            print(f"CN Compliance Result: {result.get('compliant', False)}")
            print(f"File saved to disk: {result.get('saved_to_disk', False)}")
        
        # Example 3: Legacy tag endpoint (for backward compatibility)
        print("\n=== Legacy Tag Endpoint ===")
        image_url = "https://example.com/test-image.jpg"  # Replace with actual URL
        
        tag_result = client.tag(
            image_url=image_url,
            region="EU",
            watermark_text="AI Generated Content",
            watermark_logo=True,
            metadata_level="detailed"
        )
        
        print(f"Tag Result: {tag_result}")
        
        # Example 4: Download a processed file
        print("\n=== File Download ===")
        try:
            filename = "example_processed_image.jpg"  # Replace with actual filename
            file_content = client.download_file(filename)
            with open(f"downloaded_{filename}", "wb") as f:
                f.write(file_content)
            print(f"File downloaded successfully: downloaded_{filename}")
        except Exception as e:
            print(f"Download failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        client.close()

if __name__ == "__main__":
    main()