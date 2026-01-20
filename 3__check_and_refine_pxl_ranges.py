import fitz  # PyMuPDF
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def refine_crop_region(pdf_path, page_num, x_start, x_end, y_start, y_end, zoom=2.0):
    """
    Display existing crop region and allow refinement by clicking new boundaries.
    Click twice: first for top-left corner, then for bottom-right corner.
    The new coordinates will be relative to the original crop region.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    # Get the initial crop
    rect = fitz.Rect(x_start, y_start, x_end, y_end)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    
    print(f"Current crop region (PDF space):")
    print(f"  X: {x_start:.1f} to {x_end:.1f}")
    print(f"  Y: {y_start:.1f} to {y_end:.1f}")
    print(f"Cropped image size: {pix.width} x {pix.height} pixels")
    print("\nClick twice to refine: 1) New top-left corner, 2) New bottom-right corner")
    
    fig, ax = plt.subplots(figsize=(12, 16))
    ax.imshow(img)
    ax.set_title(f"Page {page_num} - Current Crop Region\nClick to refine boundaries")
    
    coords = []
    rect_patch = None
    
    def onclick(event):
        nonlocal rect_patch
        if event.inaxes != ax:
            return
        
        x, y = int(event.xdata), int(event.ydata)
        coords.append((x, y))
        
        # Plot the clicked point
        ax.plot(x, y, 'ro', markersize=10)
        
        if len(coords) == 1:
            print(f"New top-left corner (pixel): ({x}, {y})")
            ax.set_title(f"Page {page_num} - Now click new bottom-right corner")
        elif len(coords) == 2:
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            
            # Draw rectangle showing refined region
            if rect_patch:
                rect_patch.remove()
            rect_patch = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                          linewidth=2, edgecolor='lime', facecolor='none')
            ax.add_patch(rect_patch)
            
            # Convert pixel coordinates to PDF coordinates
            # Pixels are relative to the cropped region, need to add back original offset
            new_pdf_x1 = x_start + (x1 / zoom)
            new_pdf_y1 = y_start + (y1 / zoom)
            new_pdf_x2 = x_start + (x2 / zoom)
            new_pdf_y2 = y_start + (y2 / zoom)
            
            print(f"New bottom-right corner (pixel): ({x2}, {y2})")
            print(f"\nRefined crop coordinates (PDF space):")
            print(f"X_START = {min(new_pdf_x1, new_pdf_x2):.1f}")
            print(f"X_END = {max(new_pdf_x1, new_pdf_x2):.1f}")
            print(f"Y_START = {min(new_pdf_y1, new_pdf_y2):.1f}")
            print(f"Y_END = {max(new_pdf_y1, new_pdf_y2):.1f}")
            
            ax.set_title(f"Page {page_num} - Refined region (green box) - Close to continue")
        
        fig.canvas.draw()
    
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
    if len(coords) == 2:
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        
        # Convert to PDF coordinates relative to original crop
        new_pdf_x1 = x_start + (x1 / zoom)
        new_pdf_y1 = y_start + (y1 / zoom)
        new_pdf_x2 = x_start + (x2 / zoom)
        new_pdf_y2 = y_start + (y2 / zoom)
        
        return {
            'x_start': min(new_pdf_x1, new_pdf_x2),
            'x_end': max(new_pdf_x1, new_pdf_x2),
            'y_start': min(new_pdf_y1, new_pdf_y2),
            'y_end': max(new_pdf_y1, new_pdf_y2),
            'zoom': zoom
        }
    return None


def preview_crop(pdf_path, page_num, x_start, x_end, y_start, y_end, zoom=2.0):
    """Preview the cropped region"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    rect = fitz.Rect(x_start, y_start, x_end, y_end)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    
    plt.figure(figsize=(10, 12))
    plt.imshow(img)
    plt.title(f"Final Preview - Page {page_num}\nRegion: ({x_start:.1f}, {y_start:.1f}) to ({x_end:.1f}, {y_end:.1f})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    print(f"Final cropped image size: {pix.width} x {pix.height} pixels")


# Usage example
pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"

# Example: Use coordinates from your previous selection
# Replace these with your actual values from 2__define_pxl_ranges.py
page_number = 1
initial_coords = {'x_start': 121.0, 'x_end': 377.0, 'y_start': 0.5, 'y_end': 1222.0, 'zoom': 2.0}

# Refine the region
refined_coords = refine_crop_region(
    pdf_file, 
    page_number,
    initial_coords['x_start'],
    initial_coords['x_end'],
    initial_coords['y_start'],
    initial_coords['y_end'],
    initial_coords['zoom']
)

# Preview the refined result
if refined_coords:
    preview_crop(
        pdf_file, 
        page_number,
        refined_coords['x_start'],
        refined_coords['x_end'],
        refined_coords['y_start'],
        refined_coords['y_end'],
        refined_coords['zoom']
    )