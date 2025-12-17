"""
Poppler Check and Setup Script
Run this to verify poppler installation
"""
import subprocess
import sys
import os

def check_poppler():
    """Check if poppler is installed and accessible"""
    print("=" * 60)
    print("Poppler Installation Check")
    print("=" * 60)
    
    # Try to run pdftoppm
    try:
        result = subprocess.run(['pdftoppm', '-v'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0 or 'poppler' in result.stderr.lower():
            print("✅ Poppler is installed!")
            print(f"\nVersion info:\n{result.stderr}")
            return True
        else:
            print("❌ Poppler command ran but returned error")
            return False
            
    except FileNotFoundError:
        print("❌ Poppler NOT FOUND in PATH")
        print("\nPoppler is required for PDF processing.")
        print("\nInstallation options:")
        print("\n1. Using Conda (Recommended):")
        print("   conda install -c conda-forge poppler")
        print("\n2. Manual Installation (Windows):")
        print("   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("   - Extract to: C:\\Program Files\\poppler")
        print("   - Add to PATH: C:\\Program Files\\poppler\\bin")
        print("\n3. Using Chocolatey:")
        print("   choco install poppler")
        print("\nAfter installation, restart your terminal and run this script again.")
        return False
        
    except Exception as e:
        print(f"❌ Error checking poppler: {e}")
        return False

def check_pdf2image():
    """Check if pdf2image package is installed"""
    try:
        import pdf2image
        print("\n✅ pdf2image Python package is installed")
        print(f"   Version: {pdf2image.__version__ if hasattr(pdf2image, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        print("\n❌ pdf2image package not installed")
        print("   Install with: pip install pdf2image")
        return False

def test_pdf_conversion():
    """Test PDF to image conversion"""
    try:
        from pdf2image import convert_from_path
        print("\n📄 Testing PDF conversion...")
        
        # Create a test PDF
        test_pdf = "test_sample.pdf"
        if not os.path.exists(test_pdf):
            print("   No test PDF found. Skipping conversion test.")
            return True
        
        print(f"   Converting: {test_pdf}")
        images = convert_from_path(test_pdf, first_page=1, last_page=1)
        print(f"   ✅ Successfully converted! Got {len(images)} image(s)")
        return True
        
    except Exception as e:
        print(f"   ❌ Conversion failed: {e}")
        if 'Unable to get page count' in str(e):
            print("\n   This error means poppler is not properly installed or not in PATH.")
        return False

def main():
    """Main check routine"""
    poppler_ok = check_poppler()
    pdf2image_ok = check_pdf2image()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if poppler_ok and pdf2image_ok:
        print("✅ All checks passed! PDF processing should work.")
        test_pdf_conversion()
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick Fix Steps:")
        print("1. Install poppler (see instructions above)")
        print("2. Ensure pip install pdf2image is run")
        print("3. Restart your terminal")
        print("4. Run this script again")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
