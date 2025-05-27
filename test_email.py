"""
Test email distribution using an existing markdown file
"""
import os
import sys
from distributor import MarkdownDistributor

def test_email_distribution(markdown_file_path):
    """
    Test email distribution with an existing markdown file
    
    Args:
        markdown_file_path: Path to the markdown file to send
    """
    print(f"Testing email distribution with file: {markdown_file_path}")
    
    # Check if file exists
    if not os.path.exists(markdown_file_path):
        print(f"Error: File not found: {markdown_file_path}")
        return
    
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Create distributor
    distributor = MarkdownDistributor()
    
    # Convert to HTML
    try:
        print("Converting markdown to HTML...")
        html_content = distributor.markdown_to_html(markdown_content)
    except Exception as e:
        print(f"Error converting to HTML: {str(e)}")
        return
    
    # Try both email methods
    print("\n=== Testing Standard SMTP ===")
    smtp_result = distributor.send_email_smtp(markdown_content, html_content)
    
    print("\n=== Testing Yagmail ===")
    yagmail_result = distributor.send_email_yagmail(markdown_content, html_content)
    
    # Summary
    print("\n=== Results ===")
    print(f"SMTP Email: {'Success' if smtp_result else 'Failed'}")
    print(f"Yagmail: {'Success' if yagmail_result else 'Failed'}")

if __name__ == "__main__":
    # Use latest file in output directory if no file specified
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        output_dir = "output"
        if not os.path.exists(output_dir):
            print(f"Error: Output directory not found: {output_dir}")
            sys.exit(1)
            
        # Get most recent file
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".md")]
        if not files:
            print(f"No markdown files found in {output_dir}")
            sys.exit(1)
            
        file_path = max(files, key=os.path.getmtime)
        print(f"Using most recent file: {file_path}")
    
    test_email_distribution(file_path) 