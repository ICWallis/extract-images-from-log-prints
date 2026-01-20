import fitz  # PyMuPDF
from PIL import Image
import io
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def interactive_crop_selector(pdf_path, page_num, zoom=2.0):
    """
    Interactive tool to select crop region by clicking on the image.
    Click twice: first for top-left corner, then for bottom-right corner.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    
    print(f"Page {page_num} dimensions: {pix.width} x {pix.height}")
    print("Click twice to define crop region: 1) Top-left corner, 2) Bottom-right corner")
    
    fig, ax = plt.subplots(figsize=(12, 16))
    ax.imshow(img)
    ax.set_title(f"Page {page_num} - Click to define crop region")
    
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
            print(f"Top-left corner: ({x}, {y})")
            ax.set_title(f"Page {page_num} - Now click bottom-right corner")
        elif len(coords) == 2:
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            
            # Draw rectangle
            if rect_patch:
                rect_patch.remove()
            rect_patch = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                          linewidth=2, edgecolor='r', facecolor='none')
            ax.add_patch(rect_patch)
            
            # Convert back to PDF coordinates (divide by zoom)
            pdf_x1, pdf_y1 = x1 / zoom, y1 / zoom
            pdf_x2, pdf_y2 = x2 / zoom, y2 / zoom
            
            print(f"Bottom-right corner: ({x2}, {y2})")
            print(f"\nCrop coordinates (PDF space):")
            print(f"X_START = {min(pdf_x1, pdf_x2)}")
            print(f"X_END = {max(pdf_x1, pdf_x2)}")
            print(f"Y_START = {min(pdf_y1, pdf_y2)}")
            print(f"Y_END = {max(pdf_y1, pdf_y2)}")
            print(f"ZOOM = {zoom}")
            
            ax.set_title(f"Page {page_num} - Region selected (close window to continue)")
        
        fig.canvas.draw()
    
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
    if len(coords) == 2:
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        # Return coordinates in PDF space (divided by zoom)
        return {
            'x_start': min(x1, x2) / zoom,
            'x_end': max(x1, x2) / zoom,
            'y_start': min(y1, y2) / zoom,
            'y_end': max(y1, y2) / zoom,
            'zoom': zoom
        }
    return None


def preview_crop(pdf_path, page_num, x_start, x_end, y_start, y_end, zoom=2.0):
    """Preview the cropped region"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    # Crop and render with the same zoom factor
    rect = fitz.Rect(x_start, y_start, x_end, y_end)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    
    # Display cropped result
    plt.figure(figsize=(10, 12))
    plt.imshow(img)
    plt.title(f"Cropped Preview - Page {page_num}\nRegion: ({x_start:.1f}, {y_start:.1f}) to ({x_end:.1f}, {y_end:.1f})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    print(f"Cropped image size: {pix.width} x {pix.height} pixels")


pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"


# Interactive selection
page_number = 1  # Start with page 1 (first data page)
crop_coords = interactive_crop_selector(pdf_file, page_number)


# Preview the crop (run after interactive selection)
if crop_coords:
    preview_crop(pdf_file, page_number, 
                 crop_coords['x_start'], crop_coords['x_end'],
                 crop_coords['y_start'], crop_coords['y_end'],
                 crop_coords['zoom'])
    
    # Print the dictionary for easy copy-paste to next script
    print("\n--- Copy this for refinement script ---")
    print(f"initial_coords = {crop_coords}")


