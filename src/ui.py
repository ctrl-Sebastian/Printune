import io
import pyvista as pv
from customtkinter import *
import requests
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import threading
import src.utils as utils
import src.modeling as modeling
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import glob

class TagifyApp(CTk):
    def __init__(self):
        super().__init__()
        set_appearance_mode("dark")
        #self.iconbitmap(utils.resource_path("icon.ico"))
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.window_width = int(self.screen_width * 0.8)
        self.window_height = int(self.screen_height * 0.8)
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.title("Tagify")

        # State
        self.spotify_data = None
        self.bar_heights = None
        self.selected_base_model = None
        self.base_model_buttons = []
        self.base_model_paths = []

        # UI
        self.create_frames()
        self.show_home_page()

    def create_frames(self):
        """
        Create and configure all frames and widgets for the application.
        """
        # Create homepage frame
        self.home_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create title
        title = CTkLabel(self.home_frame, text="Tagify", font=("Arial bold", 64), text_color="#1ED760")
        title.place(relx=0.5, rely=0.4, anchor=CENTER)

        # Create URL input field
        self.url_input = CTkEntry(
            self.home_frame, 
            placeholder_text="Enter URL", 
            width=(self.window_width // 3),
            height=40,
            corner_radius=12,
            font=("Arial bold", 18),
            fg_color="gray20",
            text_color="#1ED760",
            border_width=2,
            border_color="gray50"
        )
        self.url_input.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Create submit button
        submit_url_btn = CTkButton(
            self.home_frame, 
            text="Submit URL",
            font=("Arial bold", 18),
            fg_color="transparent",
            border_width=2,
            hover_color="#1ED760",
            corner_radius=12,
            border_color="#1ED760",
            text_color="white",
            height=40,
            width=(self.window_width // 4),
            command=self.process_url
        )
        submit_url_btn.place(relx=0.5, rely=0.65, anchor=CENTER)
        
        # Create developer info
        developer_name = CTkLabel(
            self.home_frame, 
            text="Developed by Sebastian De Leon", 
            font=("Arial", 16),
            cursor="hand2"
        )
        developer_name.place(relx=0.5, rely=0.9, anchor=CENTER)
        developer_name.bind("<Button-1>", lambda e: utils.open_link("https://sebastiandeleonportfolio.vercel.app/"))
        
        # Create customization frame
        self.customization_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.customization_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid for customization frame to have two columns
        self.customization_frame.grid_columnconfigure(0, weight=1)
        self.customization_frame.grid_columnconfigure(1, weight=2)
        self.customization_frame.grid_rowconfigure(0, weight=1)
        
        # Create left panel (customization options)
        self.left_panel = CTkFrame(self.customization_frame)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.grid_rowconfigure(2, weight=1)  # For base model grid to expand
        
        # Add some sample customization options (placeholder)
        options_label = CTkLabel(self.left_panel, text="Customization Options", font=("Arial", 20))
        options_label.pack(pady=20, padx=10)
        
        # --- Base Model Selection ---
        base_models_dir = utils.resource_path("base_models")
        self.base_models_dir = base_models_dir  # Store for later use
        self.base_models_per_page = 6  # Number of models per page
        self.base_model_page = 0  # Current page

        def scan_base_models():
            step_files = glob.glob(os.path.join(self.base_models_dir, "*.step"))
            self.base_model_paths = step_files
            return step_files

        base_model_btn_frame = CTkFrame(self.left_panel, fg_color="transparent")
        base_model_btn_frame.pack(pady=0, padx=0, fill="none", expand=True)
        base_model_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)  # 3 columns
        self.base_model_btn_frame = base_model_btn_frame  # Store reference
        self.selected_base_model = scan_base_models()[0]
        # Do NOT create any base model buttons here!
        # Only call update_base_model_buttons() after scan_base_models()

        def update_base_model_buttons():
            # Only destroy base model buttons (not the whole left panel)
            for btn in getattr(self, "base_model_buttons", []):
                btn.destroy()
            self.base_model_buttons = []
            # Remove custom button if exists
            if hasattr(self, "load_custom_btn"):
                self.load_custom_btn.destroy()
            # Remove pagination buttons if exist
            if hasattr(self, "pagination_frame"):
                self.pagination_frame.destroy()

            step_files = scan_base_models()
            total_pages = max(1, (len(step_files) + self.base_models_per_page - 1) // self.base_models_per_page)
            self.base_model_page = min(self.base_model_page, total_pages - 1)
            start_idx = self.base_model_page * self.base_models_per_page
            end_idx = start_idx + self.base_models_per_page
            page_files = step_files[start_idx:end_idx]

            btn_size = min(max(self.window_width // 15, 80), 100)
            base_model_btn_frame = self.base_model_btn_frame  # Use stored reference
            # Only destroy button widgets in the frame (not the frame itself)
            for widget in base_model_btn_frame.winfo_children():
                widget.destroy()
            base_model_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
            for idx, step_path in enumerate(page_files):
                img_path = os.path.splitext(step_path)[0] + ".png"
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    w, h = img.size
                    min_dim = min(w, h)
                    left = (w - min_dim) // 2
                    top = (h - min_dim) // 2
                    img = img.crop((left, top, left + min_dim, top + min_dim))
                    img = img.resize((btn_size, btn_size))
                else:
                    img = Image.new("RGB", (btn_size, btn_size), color="gray")
                tk_img = CTkImage(light_image=img, dark_image=img, size=(btn_size, btn_size))
                btn = CTkButton(
                    base_model_btn_frame,
                    image=tk_img,
                    text="",
                    width=btn_size,
                    height=btn_size,
                    fg_color="gray20",
                    border_width=2,
                    corner_radius=12,
                    border_color="green" if self.selected_base_model == step_path else "gray50",
                    command=lambda i=start_idx+idx: on_base_model_select(i)
                )
                row, col = divmod(idx, 3)
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.base_model_buttons.append(btn)
                base_model_btn_frame.grid_rowconfigure(row, weight=1)

            # Add custom base model button
            custom_btn_idx = len(page_files)
            row, col = divmod(custom_btn_idx, 3)
            load_custom_btn = CTkButton(
                base_model_btn_frame,
                text="+",
                width=btn_size,
                height=btn_size,
                fg_color="gray20",
                border_width=3,
                corner_radius=12,
                border_color="gray50",
                command=load_custom_step
            )
            load_custom_btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.load_custom_btn = load_custom_btn
            base_model_btn_frame.grid_rowconfigure(row, weight=1)

            # Pagination controls (place directly below base model buttons)
            pagination_frame = CTkFrame(self.left_panel, fg_color="transparent")
            # Use pack_forget to remove if it exists elsewhere
            pagination_frame.pack_forget()
            # Place below the base_model_btn_frame using .pack (before download button)
            pagination_frame.pack(after=self.base_model_btn_frame, pady=(5, 0))
            self.pagination_frame = pagination_frame
            prev_btn = CTkButton(pagination_frame, text="<", width=32, command=go_prev_page)
            prev_btn.pack(side="left", padx=5)
            page_label = CTkLabel(pagination_frame, text=f"Page {self.base_model_page+1}/{total_pages}")
            page_label.pack(side="left", padx=5)
            next_btn = CTkButton(pagination_frame, text=">", width=32, command=go_next_page)
            next_btn.pack(side="left", padx=5)
            prev_btn.configure(state="normal" if self.base_model_page > 0 else "disabled")
            next_btn.configure(state="normal" if self.base_model_page < total_pages-1 else "disabled")

        def go_prev_page():
            if self.base_model_page > 0:
                self.base_model_page -= 1
                update_base_model_buttons()

        def go_next_page():
            step_files = scan_base_models()
            total_pages = max(1, (len(step_files) + self.base_models_per_page - 1) // self.base_models_per_page)
            if self.base_model_page < total_pages-1:
                self.base_model_page += 1
                update_base_model_buttons()

        def on_base_model_select(idx):
            step_files = scan_base_models()
            if 0 <= idx < len(step_files):
                self.selected_base_model = step_files[idx]
                update_base_model_buttons()
                self.update_model_preview()

        def load_custom_step():
            file_path = filedialog.askopenfilename(
                title="Select STEP file",
                filetypes=[("STEP files", "*.step")]
            )
            if file_path:
                # Copy the file to base_models folder
                import shutil
                dest_path = os.path.join(self.base_models_dir, os.path.basename(file_path))
                try:
                    shutil.copy(file_path, dest_path)
                    self.selected_base_model = dest_path
                    update_base_model_buttons()
                    self.update_model_preview()
                except Exception as e:
                    print(f"Failed to copy file: {e}")

        scan_base_models()
        update_base_model_buttons()
        
        # Add a button below the grid to download the blank base model
        def download_blank_model():
            blank_model_path = os.path.join("assets", "blank_base_model.step")
            if not os.path.exists(blank_model_path):
                print("Blank model not found.")
                return
            save_path = filedialog.asksaveasfilename(
                defaultextension=".step",
                filetypes=[("STEP files", "*.step")],
                title="Save Blank Base Model As",
                initialfile="blank_base_model.step"
            )
            if save_path:
                with open(blank_model_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                print(f"Blank base model saved to {save_path}")

        download_blank_btn = CTkButton(
            self.left_panel,
            text="Download Blank Base Model",
            font=("Arial", 14),
            border_width=1,
            corner_radius=12,
            fg_color="gray30",
            hover_color="#1ED760",
            border_color="#1ED760",
            text_color="white",
            width=(self.window_width // 4),
            height=32,
            command=download_blank_model
        )
        download_blank_btn.pack(pady=(10, 0), padx=10)
        # --- End Base Model Selection ---
        
        # Add an apply button
        generate_btn = CTkButton(
            self.left_panel, 
            text="Generate Model",
            font=("Arial bold", 18),
            border_width=2,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#1ED760",
            border_color="#1ED760",
            text_color="white",
            width=(self.window_width // 4),
            height=40,
            command=self.export_model
        )
        generate_btn.pack(pady=20, padx=10)
        
        # Add back button
        back_btn = CTkButton(
            self.left_panel, 
            text="Back to Home",
            font=("Arial bold", 18),
            border_width=2,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#1ED760",
            border_color="#1ED760",
            text_color="white",
            width=(self.window_width // 4),
            height=40,
            command=self.show_home_page
        )
        back_btn.pack(pady=5, padx=10)
        
        # Create right panel (preview)
        self.right_panel = CTkFrame(self.customization_frame)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Add preview label
        preview_label = CTkLabel(self.right_panel, text="Model Preview", font=("Arial", 20))
        preview_label.pack(pady=20)
        
        # The model preview
        self.preview_frame = CTkFrame(self.right_panel, fg_color="gray50")
        self.preview_frame.pack(expand=True, fill="both", pady=10, padx=10) 
        
        # Configure grid for root window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Make app respond to window resizing
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        # Redraw base model buttons with new size if window size changes significantly
        new_btn_size = min(max(self.winfo_width() // 15, 80), 160)
        if hasattr(self, "_last_btn_size") and self._last_btn_size == new_btn_size:
            return
        self._last_btn_size = new_btn_size
        # Remove old buttons
        for btn in getattr(self, "base_model_buttons", []):
            btn.destroy()
        self.base_model_buttons = []
        # Remove custom button if exists
        if hasattr(self, "load_custom_btn"):
            self.load_custom_btn.destroy()
        # Recreate buttons for the current page only
        base_model_btn_frame = self.base_model_btn_frame
        for widget in base_model_btn_frame.winfo_children():
            widget.destroy()
        base_model_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        # Pagination logic
        step_files = self.base_model_paths
        total_pages = max(1, (len(step_files) + self.base_models_per_page - 1) // self.base_models_per_page)
        self.base_model_page = min(self.base_model_page, total_pages - 1)
        start_idx = self.base_model_page * self.base_models_per_page
        end_idx = start_idx + self.base_models_per_page
        page_files = step_files[start_idx:end_idx]
        for idx, step_path in enumerate(page_files):
            img_path = os.path.splitext(step_path)[0] + ".png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                w, h = img.size
                min_dim = min(w, h)
                left = (w - min_dim) // 2
                top = (h - min_dim) // 2
                img = img.crop((left, top, left + min_dim, top + min_dim))
                img = img.resize((new_btn_size, new_btn_size))
            else:
                img = Image.new("RGB", (new_btn_size, new_btn_size), color="gray")
            tk_img = CTkImage(light_image=img, dark_image=img, size=(new_btn_size, new_btn_size))
            btn = CTkButton(
                base_model_btn_frame,
                image=tk_img,
                text="",
                width=new_btn_size + 4,
                height=new_btn_size + 4,
                fg_color="gray20",
                border_width=3,
                border_color="green" if self.selected_base_model == step_path else "gray50",
                command=lambda i=start_idx+idx: self._on_base_model_select_resize(i)
            )
            row, col = divmod(idx, 3)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.base_model_buttons.append(btn)
            base_model_btn_frame.grid_rowconfigure(row, weight=1)
        # Custom button
        custom_btn_idx = len(page_files)
        row, col = divmod(custom_btn_idx, 3)
        load_custom_btn = CTkButton(
            base_model_btn_frame,
            text="+",
            width=new_btn_size + 4,
            height=new_btn_size + 4,
            fg_color="gray20",
            border_width=3,
            border_color="gray50",
            command=self.load_custom_btn.cget("command") if hasattr(self, "load_custom_btn") else None
        )
        load_custom_btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        self.load_custom_btn = load_custom_btn
        base_model_btn_frame.grid_rowconfigure(row, weight=1)
        # (Optional: update pagination controls position/size if needed)

    def _on_base_model_select_resize(self, idx):
        self.selected_base_model = self.base_model_paths[idx]
        for i, btn in enumerate(self.base_model_buttons):
            btn.configure(border_color="green" if i == idx else "gray50")
        self.update_model_preview()
    
    def show_home_page(self):
        # Show home page and hide customization page
        self.customization_frame.grid_remove()
        self.home_frame.grid()
    
    def show_customization_page(self):
        # Show customization page and hide home page
        self.home_frame.grid_remove()
        self.customization_frame.grid()
    
    def process_url(self):
        # Get URL from input field
        share_link = self.url_input.get()
        
        # Process the URL to get Spotify data
        data = utils.get_link_data(share_link)
        
        if len(data) != 2:
            print("Something went wrong while parsing the URL.")
            return
        
        # Store the data for later use
        self.spotify_data = data
        
        # Download Spotify Code and process it to get bar heights
        code_URL = f"https://www.spotifycodes.com/downloadCode.php?uri=jpeg%2F000000%2Fwhite%2F640%2Fspotify%3A{data[0]}%3A{data[1]}"
        
        r = requests.get(code_URL)
        
        if not r.ok or not r.content:
            print("Something went wrong while fetching the Spotify code.")
            return
        
        # Process image to get bar heights
        img = Image.open(io.BytesIO(r.content)).crop((160, 0, 640-31, 160))
        width, height = img.size
        pix = img.load()
        
        bar_heights = []
        max_height_of_single_bar = 0
        
        for x in range(width):
            at_bar = False
            curr_height = 0
            
            for y in range(height):
                if pix[x,y][0] > 20 or pix[x,y][1] > 20 or pix[x,y][2] > 20:
                    at_bar = True
                    curr_height += 1
            
            if at_bar and curr_height > max_height_of_single_bar:
                max_height_of_single_bar = curr_height/20
            elif not at_bar and max_height_of_single_bar > 0:
                bar_heights.append(max_height_of_single_bar)
                max_height_of_single_bar = 0
        
        # Store bar heights for later use
        self.bar_heights = bar_heights
        
        print(f"There are {len(bar_heights)} bars of heights {bar_heights}")
        
        # Switch to the customization page
        self.show_customization_page()
        
        # Initialize the 3D preview
        self.update_model_preview()
    
    def export_model(self):
        if not self.bar_heights or not self.selected_base_model:
            print("No data to generate model from")
            return
        
        model = modeling.generate_model_without_export(self.bar_heights, self.selected_base_model)
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".stl",
            filetypes=[("STL files", "*.stl")],
            title="Save Model As"
        )
        if not file_path:
            print("Export cancelled.")
            return

        # Export model
        modeling.export_model(model, file_path)
        print(f"Model exported as {file_path}")

    def show_loading_gif(self):
        """Display a loading GIF in the preview frame (optimized for speed)."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        gif_path = utils.resource_path("..\\assets\\loading.gif")
        if not os.path.exists(gif_path):
            label = CTkLabel(self.preview_frame, text="Loading...", font=("Arial", 18))
            label.pack(expand=True)
            return

        # Use a regular tkinter Label for GIF animation
        from tkinter import Label
        try:
            gif = Image.open(gif_path)
            # Only load the first few frames to speed up initial display
            frames = []
            for _ in range(10):  # Load up to 10 frames quickly
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(gif.tell() + 1)
        except Exception:
            frames = []

        if not frames:
            label = CTkLabel(self.preview_frame, text="Loading...", font=("Arial", 18))
            label.pack(expand=True)
            return

        gif_label = Label(self.preview_frame, bg="black")
        gif_label.pack(expand=True, fill="both")
        self._gif_frames = frames
        self._gif_label = gif_label
        self._gif_frame_idx = 0

        def animate():
            if hasattr(self, "_gif_frames"):
                frame = self._gif_frames[self._gif_frame_idx]
                self._gif_label.configure(image=frame)
                self._gif_frame_idx = (self._gif_frame_idx + 1) % len(self._gif_frames)
                self._gif_label.after(60, animate)
        animate()

    def update_model_preview(self):
        """Update the 3D preview in the preview frame with a loading indicator."""
        

        def generate_and_show():
            # Generate the model in memory
            model = modeling.generate_model_without_export(self.bar_heights, self.selected_base_model)
            if not model:
                print("No model to preview.")
                # Remove GIF and show error
                self.after(0, lambda: [
                    widget.destroy() for widget in self.preview_frame.winfo_children()
                ])
                self.after(0, lambda: CTkLabel(self.preview_frame, text="No model to preview.", font=("Arial", 18)).pack(expand=True))
                return

            # Export the model to a temporary STL file
            temp_stl_path = utils.resource_path("temp_preview_model.stl")
            modeling.export_model(model, temp_stl_path)

            # Use PyVista to render the STL file and save it as an image
            plotter = pv.Plotter(off_screen=True)
            plotter.add_mesh(pv.read(temp_stl_path), color="white")
            plotter.set_background("black")
            temp_image_path = "temp_preview_image.png"
            plotter.screenshot(temp_image_path)
            plotter.close()

            # Display the image in the preview frame using matplotlib
            def show_image():
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                fig = Figure(figsize=(5, 5), dpi=100)
                ax = fig.add_subplot(111)
                img = plt.imread(temp_image_path)
                ax.imshow(img)
                ax.axis("off")  # Hide axes

                canvas = FigureCanvasTkAgg(fig, master=self.preview_frame)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(expand=True, fill="both", pady=10, padx=10)

                # Clean up temporary files
                os.remove(temp_stl_path)
                os.remove(temp_image_path)

            self.after(0, show_image)

        # Run model generation in a background thread
        threading.Thread(target=generate_and_show, daemon=True).start()


if __name__ == "__main__":
    app = TagifyApp()
    app.mainloop()