import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageFilter
import cv2
import numpy as np
import logging
import threading
import sys
import subprocess
import psutil  # To get system memory info

# Configure logging to write to 'All_Logs.log' file and console
logging.basicConfig(
    level=logging.INFO,  # Adjust logging level as needed
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("All_Logs.log"),
        logging.StreamHandler()
    ]
)

class OhBotArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OhBot Art - Futuristic Image Processor")
        self.root.configure(bg="#f0f0f0")  # Lighter background color

        # Open the window maximized by default
        self.root.state('zoomed')  # For Windows

        # Set up style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#f0f0f0', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('TButton', background='#e0e0e0', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('TLabel', background='#f0f0f0', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('TEntry', background='#ffffff', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('Horizontal.TScale', background='#f0f0f0')
        self.style.configure('TRadiobutton', background='#f0f0f0', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('TMenubutton', background='#e0e0e0', foreground='#000000', font=('Helvetica', 10))
        self.style.configure('TFrame', background='#f0f0f0')

        self.filepath = None
        self.image = None
        self.processed_image = None
        self.original_aspect_ratio = None

        # UI layout
        self.create_ui()
        logging.info("Application initialized.")

    def create_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Configure grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # File upload section
        self.main_frame.rowconfigure(1, weight=1)  # Image previews
        self.main_frame.rowconfigure(2, weight=0)  # Controls
        self.main_frame.rowconfigure(3, weight=0)  # Download options

        # File upload section
        file_frame = ttk.Frame(self.main_frame)
        file_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky='we')
        file_frame.columnconfigure(0, weight=1)
        upload_btn = ttk.Button(file_frame, text="Upload Image", command=self.upload_image)
        upload_btn.pack(side=tk.LEFT, padx=5)
        upload_btn_ttp = CreateToolTip(upload_btn, "Click to upload an image.")

        # Original and Processed Image views
        self.image_frame = ttk.Frame(self.main_frame)
        self.image_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.columnconfigure(1, weight=1)
        self.image_frame.rowconfigure(1, weight=1)

        # Original Image
        original_header = ttk.Label(self.image_frame, text="Original Image", font=('Helvetica', 12, 'bold'))
        original_header.grid(row=0, column=0, pady=5)
        self.original_canvas = tk.Canvas(self.image_frame, bg="#d0d0d0", highlightthickness=0)
        self.original_canvas.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

        # Processed Image
        processed_header = ttk.Label(self.image_frame, text="Processed Image", font=('Helvetica', 12, 'bold'))
        processed_header.grid(row=0, column=1, pady=5)
        self.processed_canvas = tk.Canvas(self.image_frame, bg="#d0d0d0", highlightthickness=0)
        self.processed_canvas.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

        # Controls Frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky='we')
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=1)
        controls_frame.columnconfigure(3, weight=1)  # Added for Reset button alignment

        # Sliders for detail, thickness, brightness
        options_frame = ttk.LabelFrame(controls_frame, text="Adjustments")
        options_frame.grid(row=0, column=0, padx=10, sticky='we')
        options_frame.columnconfigure(1, weight=1)

        self.detail_var = tk.DoubleVar(value=1.0)
        detail_label = ttk.Label(options_frame, text="Details")
        detail_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        detail_scale = ttk.Scale(options_frame, from_=0.5, to=5, orient="horizontal", variable=self.detail_var, command=self.update_image)
        detail_scale.grid(row=0, column=1, padx=5, sticky='we')
        CreateToolTip(detail_scale, "Adjust the level of detail in edge detection.")

        self.thickness_var = tk.IntVar(value=1)
        thickness_label = ttk.Label(options_frame, text="Thickness")
        thickness_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        thickness_scale = ttk.Scale(options_frame, from_=1, to=10, orient="horizontal", variable=self.thickness_var, command=self.update_image)
        thickness_scale.grid(row=1, column=1, padx=5, sticky='we')
        CreateToolTip(thickness_scale, "Adjust the thickness of the edges.")

        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_label = ttk.Label(options_frame, text="Brightness")
        brightness_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        brightness_scale = ttk.Scale(options_frame, from_=0.5, to=3, orient="horizontal", variable=self.brightness_var, command=self.update_image)
        brightness_scale.grid(row=2, column=1, padx=5, sticky='we')
        CreateToolTip(brightness_scale, "Adjust the brightness of the image.")

        # Style options
        style_frame = ttk.LabelFrame(controls_frame, text="Style")
        style_frame.grid(row=0, column=1, padx=10, sticky='we')
        style_frame.columnconfigure(0, weight=1)

        self.style_var = tk.StringVar(value="smooth")
        smooth_rb = ttk.Radiobutton(style_frame, text="Smooth", variable=self.style_var, value="smooth", command=self.update_image)
        smooth_rb.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        CreateToolTip(smooth_rb, "Apply a smooth effect to the image.")

        sharp_rb = ttk.Radiobutton(style_frame, text="Sharp", variable=self.style_var, value="sharp", command=self.update_image)
        sharp_rb.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        CreateToolTip(sharp_rb, "Apply a sharp effect to the image.")

        clean_rb = ttk.Radiobutton(style_frame, text="Clean", variable=self.style_var, value="clean", command=self.update_image)
        clean_rb.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        CreateToolTip(clean_rb, "Apply a clean, binary effect to the image.")

        # Color Mode options
        color_mode_frame = ttk.LabelFrame(controls_frame, text="Color Mode")
        color_mode_frame.grid(row=0, column=2, padx=10, sticky='we')
        color_mode_frame.columnconfigure(0, weight=1)

        self.color_mode_var = tk.StringVar(value="black_on_white")
        bow_rb = ttk.Radiobutton(color_mode_frame, text="Black on White", variable=self.color_mode_var, value="black_on_white", command=self.update_image)
        bow_rb.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        CreateToolTip(bow_rb, "Black lines on white background.")

        wob_rb = ttk.Radiobutton(color_mode_frame, text="White on Black", variable=self.color_mode_var, value="white_on_black", command=self.update_image)
        wob_rb.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        CreateToolTip(wob_rb, "White lines on black background.")

        # Reset Button
        reset_btn = ttk.Button(controls_frame, text="Reset", command=self.reset_settings)
        reset_btn.grid(row=0, column=3, padx=10, pady=5)
        CreateToolTip(reset_btn, "Reset all settings to default.")

        # Download options
        download_frame = ttk.Frame(self.main_frame)
        download_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky='we')
        download_frame.columnconfigure(1, weight=1)
        download_frame.columnconfigure(3, weight=1)
        download_frame.columnconfigure(4, weight=1)  # Added for new button

        # Width and Height inputs
        ttk.Label(download_frame, text="Width (pixels)").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.width_var = tk.IntVar()
        width_entry = ttk.Entry(download_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        CreateToolTip(width_entry, "Set the width for the saved image.")

        ttk.Label(download_frame, text="Height (pixels)").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.height_var = tk.IntVar()
        height_entry = ttk.Entry(download_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        CreateToolTip(height_entry, "Set the height for the saved image.")

        # Maintain Aspect Ratio Checkbox
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(download_frame, text="Maintain Aspect Ratio", variable=self.maintain_aspect_var)
        aspect_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        CreateToolTip(aspect_check, "Toggle to maintain or ignore the original aspect ratio.")

        # Bind width and height variable changes
        self.width_var.trace_add('write', self.width_changed)
        self.height_var.trace_add('write', self.height_changed)

        # Quality options
        ttk.Label(download_frame, text="Quality").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.quality_var = tk.StringVar(value="Best")
        quality_options = ["Good", "Best", "Highest Quality"]
        self.quality_menu = ttk.Combobox(download_frame, textvariable=self.quality_var, values=quality_options, state='readonly')
        self.quality_menu.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        CreateToolTip(self.quality_menu, "Select the quality for the saved image.")

        ttk.Label(download_frame, text="Format").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.format_var = tk.StringVar(value="png")

        # Image formats
        common_formats = ['bmp', 'jpeg', 'jpg', 'png', 'tiff', 'pdf']
        self.format_menu = ttk.Combobox(download_frame, textvariable=self.format_var, values=common_formats, state='readonly')
        self.format_menu.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        CreateToolTip(self.format_menu, "Select the format to save the image.")

        # Existing Download Button
        download_btn = ttk.Button(download_frame, text="Download Image", command=self.download_image)
        download_btn.grid(row=2, column=3, padx=10, pady=5)
        CreateToolTip(download_btn, "Click to download the processed image.")

        # **New Button: Download Transparent Image**
        download_transparent_btn = ttk.Button(download_frame, text="Download Transparent", command=self.download_image_transparent)
        download_transparent_btn.grid(row=3, column=3, padx=10, pady=5)
        CreateToolTip(download_transparent_btn, "Download the image with a transparent background.")

        # Bind the configure event to adjust the canvases
        self.root.bind('<Configure>', self.resize_canvases)

    def upload_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp *.ico")])
        if filepath:
            self.filepath = filepath
            self.image = Image.open(filepath).convert("RGB")  # Ensure image is in RGB
            self.original_aspect_ratio = self.image.width / self.image.height
            self.show_image(self.original_canvas, self.image)
            self.width_var.set(self.image.width)
            self.height_var.set(self.image.height)
            self.update_image()
            logging.info(f"Image uploaded: {filepath}")

    def show_image(self, canvas, img):
        # Adjust image size to fit the canvas
        canvas.update_idletasks()  # Ensure canvas dimensions are up-to-date
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = int(self.root.winfo_width() * 0.45)
            canvas_height = int(self.root.winfo_height() * 0.6)
        img = img.copy()
        img.thumbnail((int(canvas_width), int(canvas_height)), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        canvas.img_tk = img_tk  # Keep a reference to prevent garbage collection
        canvas.delete("all")
        canvas.create_image(canvas_width // 2, canvas_height // 2, anchor="center", image=img_tk)

    def update_image(self, *args):
        if self.image:
            logging.info("Starting image processing...")
            # Process in a separate thread to keep the UI responsive
            threading.Thread(target=self.process_image).start()

    def process_image(self):
        try:
            img_np = np.array(self.image)

            # Check if the image is already grayscale
            if len(img_np.shape) == 2 or (len(img_np.shape) == 3 and img_np.shape[2] == 1):
                img_cv = img_np
                logging.info("Image is already in grayscale.")
            else:
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                logging.info("Image converted to grayscale.")

            # Adjust brightness on the grayscale image before edge detection
            if self.brightness_var.get() != 1.0:
                img_cv = cv2.convertScaleAbs(img_cv, alpha=self.brightness_var.get())
                logging.info(f"Brightness adjusted with alpha: {self.brightness_var.get()}")

            # Apply edge detection
            lower_threshold = int(50 / self.detail_var.get())
            upper_threshold = int(150 / self.detail_var.get())
            edges = cv2.Canny(img_cv, lower_threshold, upper_threshold)
            logging.info(f"Edge detection applied with thresholds: {lower_threshold}, {upper_threshold}")

            # Adjust thickness
            kernel_size = int(self.thickness_var.get())
            if kernel_size > 1:
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                edges = cv2.dilate(edges, kernel, iterations=1)
                logging.info(f"Edges dilated with kernel size: {kernel_size}")
            else:
                logging.info("No dilation applied as kernel size is 1.")

            # Style adjustments
            if self.style_var.get() == "smooth":
                edges = cv2.GaussianBlur(edges, (5, 5), 0)
                logging.info("Applied Gaussian Blur for smooth style.")
            elif self.style_var.get() == "sharp":
                # Apply a sharpening filter
                kernel_sharp = np.array([[-1, -1, -1],
                                         [-1, 9, -1],
                                         [-1, -1, -1]])
                edges = cv2.filter2D(edges, -1, kernel_sharp)
                logging.info("Applied sharpening filter for sharp style.")
            elif self.style_var.get() == "clean":
                # Apply adaptive thresholding for a clean effect
                edges = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, 11, 2)
                logging.info("Applied adaptive thresholding for clean style.")

            # Color Mode adjustments
            if self.color_mode_var.get() == "white_on_black":
                edges = cv2.bitwise_not(edges)
                logging.info("Inverted colors for white on black mode.")

            self.processed_image = Image.fromarray(edges)
            self.show_image(self.processed_canvas, self.processed_image)
            logging.info("Image processing completed and updated on canvas.")
        except Exception as e:
            logging.error(f"Error during image processing: {e}")
            messagebox.showerror("Error", f"An error occurred during image processing:\n{e}")

    def width_changed(self, *args):
        if self.maintain_aspect_var.get() and self.original_aspect_ratio:
            try:
                width = int(self.width_var.get())
                height = int(round(width / self.original_aspect_ratio))
                self.height_var.set(height)
            except ValueError:
                pass

    def height_changed(self, *args):
        if self.maintain_aspect_var.get() and self.original_aspect_ratio:
            try:
                height = int(self.height_var.get())
                width = int(round(height * self.original_aspect_ratio))
                self.width_var.set(width)
            except ValueError:
                pass

    def download_image(self):
        if not self.processed_image:
            messagebox.showwarning("Warning", "No image to download. Please upload and process an image first.")
            logging.warning("Download attempted without a processed image.")
            return

        filename = f"processed_image.{self.format_var.get()}"
        output_path = filedialog.asksaveasfilename(defaultextension=f".{self.format_var.get()}", initialfile=filename,
                                                   filetypes=[("All Supported Formats", "*.bmp;*.jpeg;*.jpg;*.png;*.tiff;*.pdf"),
                                                              ("BMP", "*.bmp"),
                                                              ("JPEG", "*.jpeg;*.jpg"),
                                                              ("PNG", "*.png"),
                                                              ("TIFF", "*.tiff"),
                                                              ("PDF", "*.pdf")])

        if output_path:
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if width > 65500 or height > 65500:
                    messagebox.showerror("Error", "Maximum supported image dimension is 65500 pixels.")
                    logging.error("Resolution exceeds maximum supported image dimension.")
                    return

                # Determine quality based on selection
                quality = self.quality_var.get()
                if quality == "Good":
                    scale_factor = 0.5
                elif quality == "Best":
                    scale_factor = 1.0
                elif quality == "Highest Quality":
                    # Determine max size based on available memory
                    mem = psutil.virtual_memory()
                    max_pixels = mem.available // 10  # Use a fraction of available memory
                    max_dimension = int(np.sqrt(max_pixels))
                    width = min(width, max_dimension)
                    height = min(height, max_dimension)
                    scale_factor = 1.0
                else:
                    scale_factor = 1.0

                img_resized = self.processed_image.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)

                # Handle PDF format
                if self.format_var.get() == 'pdf':
                    img_resized.save(output_path, "PDF", resolution=100.0)
                else:
                    img_resized.save(output_path)

                messagebox.showinfo("Saved", f"Image saved as {output_path}")
                logging.info(f"Image saved: {output_path} with dimensions: {width}x{height}")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integers for width and height.")
                logging.error("Invalid width or height value entered.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the image:\n{e}")
                logging.error(f"Error while saving the image: {e}")

    def download_image_transparent(self):
        if not self.processed_image:
            messagebox.showwarning("Warning", "No image to download. Please upload and process an image first.")
            logging.warning("Download Transparent attempted without a processed image.")
            return

        # Ensure the processed image is in RGBA mode
        img_rgba = self.processed_image.convert("RGBA")
        datas = img_rgba.getdata()

        # Create a new data list with transparency
        new_data = []
        for item in datas:
            # If the pixel is white (background), make it transparent
            # Else, make it black (or white based on color mode) opaque
            if self.color_mode_var.get() == "black_on_white":
                # In "Black on White", lines are black (0,0,0)
                if item[0] < 128 and item[1] < 128 and item[2] < 128:
                    # Line pixel: keep as black with full opacity
                    new_data.append((0, 0, 0, 255))
                else:
                    # Background pixel: make transparent
                    new_data.append((255, 255, 255, 0))
            else:
                # In "White on Black", lines are white (255,255,255)
                if item[0] > 128 and item[1] > 128 and item[2] > 128:
                    # Line pixel: keep as white with full opacity
                    new_data.append((255, 255, 255, 255))
                else:
                    # Background pixel: make transparent
                    new_data.append((0, 0, 0, 0))

        img_rgba.putdata(new_data)

        # Prompt user to save the transparent image
        output_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile="processed_image_transparent.png",
                                                   filetypes=[("PNG files", "*.png")])

        if output_path:
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if width > 65500 or height > 65500:
                    messagebox.showerror("Error", "Maximum supported image dimension is 65500 pixels.")
                    logging.error("Resolution exceeds maximum supported image dimension.")
                    return

                # Determine quality based on selection
                quality = self.quality_var.get()
                if quality == "Good":
                    scale_factor = 0.5
                elif quality == "Best":
                    scale_factor = 1.0
                elif quality == "Highest Quality":
                    # Determine max size based on available memory
                    mem = psutil.virtual_memory()
                    max_pixels = mem.available // 10  # Use a fraction of available memory
                    max_dimension = int(np.sqrt(max_pixels))
                    width = min(width, max_dimension)
                    height = min(height, max_dimension)
                    scale_factor = 1.0
                else:
                    scale_factor = 1.0

                img_resized = img_rgba.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)

                img_resized.save(output_path, "PNG")

                messagebox.showinfo("Saved", f"Transparent image saved as {output_path}")
                logging.info(f"Transparent image saved: {output_path} with dimensions: {width}x{height}")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integers for width and height.")
                logging.error("Invalid width or height value entered.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the transparent image:\n{e}")
                logging.error(f"Error while saving the transparent image: {e}")

    def resize_canvases(self, event):
        # Adjust the canvas sizes when the window is resized
        if self.image:
            self.show_image(self.original_canvas, self.image)
        if self.processed_image:
            self.show_image(self.processed_canvas, self.processed_image)

    def reset_settings(self):
        # Reset all settings to default values
        self.detail_var.set(1.0)
        self.thickness_var.set(1)
        self.brightness_var.set(1.0)
        self.style_var.set("smooth")
        self.color_mode_var.set("black_on_white")
        self.format_var.set("png")
        self.quality_var.set("Best")
        self.maintain_aspect_var.set(True)
        if self.image:
            self.width_var.set(self.image.width)
            self.height_var.set(self.image.height)
        self.update_image()
        logging.info("Settings reset to default.")

class CreateToolTip(object):
    """
    Create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        _id = self.id
        self.id = None
        if _id:
            self.widget.after_cancel(_id)

    def showtip(self, event=None):
        x = y = 0
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)    # removes the window decorations
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background='#ffffe0', relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = OhBotArtApp(root)
        root.mainloop()
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        logging.error(f"Missing package: {missing_package}")
        response = messagebox.askyesno("Missing Package", f"The package '{missing_package}' is missing. Would you like to install it?")
        if response:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", missing_package])
                messagebox.showinfo("Package Installed", f"The package '{missing_package}' has been installed. Please restart the application.")
            except Exception as install_error:
                messagebox.showerror("Installation Error", f"An error occurred while installing the package:\n{install_error}")
        else:
            messagebox.showwarning("Warning", f"The application cannot run without the '{missing_package}' package.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
