import fitz  # PyMuPDF
from PIL import Image
import io
import os

def extract_pdf_regions_to_jpg(pdf_path, output_dir):
    """
    Extract specific regions from PDF pages and save as JPG files.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted JPG files
    """
    # Configuration - ADJUST THESE VALUES
    TOTAL_DEPTH_START = 2990  # ft
    TOTAL_DEPTH_END = 8506    # ft
    TOTAL_PAGES = 196         # Pages with data (excluding first header page)
    
    # Pixel coordinates for extraction (ADJUST AFTER INSPECTION)
    X_START = 100      # Left boundary
    X_END = 1500       # Right boundary
    Y_START_NORMAL = 50      # Top boundary for normal pages
    Y_END_NORMAL = 2800      # Bottom boundary for normal pages
    
    # Special pages with headers (page numbers are 0-indexed)
    PAGES_WITH_HEADERS = {
        0: (Y_START_NORMAL, Y_END_NORMAL - 200),  # First page
        195: (Y_START_NORMAL + 200, Y_END_NORMAL)  # Second to last page
    }
    
    # Calculate depth per page
    depth_range = TOTAL_DEPTH_END - TOTAL_DEPTH_START
    depth_per_page = depth_range / TOTAL_PAGES
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Open PDF
    pdf_doc = fitz.open(pdf_path)
    
    try:
        # Skip first page (page 0), process pages 1 to 196
        for page_num in range(1, 197):
            page = pdf_doc[page_num]
            
            # Determine Y coordinates based on whether page has header
            if page_num - 1 in PAGES_WITH_HEADERS:
                y_start, y_end = PAGES_WITH_HEADERS[page_num - 1]
            else:
                y_start, y_end = Y_START_NORMAL, Y_END_NORMAL
            
            # Calculate depth range for this page
            from_depth = TOTAL_DEPTH_START + (page_num - 1) * depth_per_page
            to_depth = TOTAL_DEPTH_START + page_num * depth_per_page
            
            # Define crop rectangle (x0, y0, x1, y1)
            rect = fitz.Rect(X_START, y_start, X_END, y_end)
            
            # Render page to pixmap with crop
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat, clip=rect)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Generate filename
            filename = f"{int(from_depth)}-{int(to_depth)}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Save as JPG
            img.save(filepath, "JPEG", quality=95)
            print(f"Saved: {filename}")
            
    finally:
        pdf_doc.close()
    
    print(f"\nExtraction complete! {196} images saved to {output_dir}")


# Usage
if __name__ == "__main__":
    pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"
    output_directory = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\extracted_images"
    
    extract_pdf_regions_to_jpg(pdf_file, output_directory)





