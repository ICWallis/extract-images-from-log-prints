import fitz  # PyMuPDF
from PIL import Image
import io
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button


def interactive_crop_selector(pdf_path, page_num, zoom=2.0):
    """
    Interactive tool to select crop region by clicking on the image.
    Toggle 'Selection Mode' button to switch between navigation and selection.
    Click twice: first for top-left corner, then for bottom-right corner.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    
    print(f"Page {page_num} dimensions: {pix.width} x {pix.height}")
    print("1. Toggle 'Selection Mode' button to enable/disable selection")
    print("2. When enabled (green), click twice to define crop region")
    print("3. Toggle off (red) to use zoom/pan tools between clicks")
    
    fig, ax = plt.subplots(figsize=(12, 16))
    plt.subplots_adjust(bottom=0.15)  # Make room for button
    ax.imshow(img)
    ax.set_title(f"Page {page_num} - Toggle 'Selection Mode' to start selecting")
    
    coords = []
    rect_patch = None
    selection_enabled = [False]  # Use list to make it mutable in nested function
    cid = [None]  # Store connection ID
    
    def onclick(event):
        if not selection_enabled[0]:
            return
        
        nonlocal rect_patch
        if event.inaxes != ax:
            return
        
        x, y = int(event.xdata), int(event.ydata)
        coords.append((x, y))
        
        # Plot the clicked point
        ax.plot(x, y, 'ro', markersize=10)
        
        if len(coords) == 1:
            print(f"Top-left corner: ({x}, {y})")
            ax.set_title(f"Page {page_num} - Now click bottom-right corner (or toggle off to zoom first)")
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
            btn.label.set_text('Selection Complete')
            btn.color = 'lightblue'
            
            # Disable selection after completion
            selection_enabled[0] = False
            if cid[0] is not None:
                fig.canvas.mpl_disconnect(cid[0])
                cid[0] = None
        
        fig.canvas.draw()
    
    def toggle_selection(event):
        if len(coords) >= 2:
            # Selection is complete, don't allow toggle
            return
            
        selection_enabled[0] = not selection_enabled[0]
        
        if selection_enabled[0]:
            # Enable selection mode
            if cid[0] is None:
                cid[0] = fig.canvas.mpl_connect('button_press_event', onclick)
            btn.label.set_text('Selection ON')
            btn.color = 'lightgreen'
            
            if len(coords) == 0:
                ax.set_title(f"Page {page_num} - Click first corner (top-left)")
            else:
                ax.set_title(f"Page {page_num} - Click second corner (bottom-right)")
            print(f"Selection mode ENABLED. Clicks: {len(coords)}/2")
        else:
            # Disable selection mode
            if cid[0] is not None:
                fig.canvas.mpl_disconnect(cid[0])
                cid[0] = None
            btn.label.set_text('Selection OFF')
            btn.color = 'lightcoral'
            ax.set_title(f"Page {page_num} - Use zoom/pan tools (toggle on to continue selecting)")
            print(f"Selection mode DISABLED. Use zoom/pan tools. Clicks: {len(coords)}/2")
        
        fig.canvas.draw()
    
    # Add toggle button
    ax_button = plt.axes([0.35, 0.05, 0.3, 0.05])
    btn = Button(ax_button, 'Selection OFF')
    btn.color = 'lightcoral'
    btn.on_clicked(toggle_selection)
    
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
page_number = 195  # Start with page 1 (first data page)
crop_coords = interactive_crop_selector(pdf_file, page_number)


# Preview the crop (run after interactive selection)
if crop_coords:
    preview_crop(pdf_file, page_number, 
                 crop_coords['x_start'], crop_coords['x_end'],
                 crop_coords['y_start'], crop_coords['y_end'],
                 crop_coords['zoom'])
    
    # Print the dictionary for easy copy-paste to next script
    print("\n--- Copy this for refinement script ---")
    print(f"pixel_coords = {crop_coords}")