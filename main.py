from customtkinter import *
import cadquery as cq
import requests
import io
from PIL import Image
import utils
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import glob
from tkinter import filedialog

class TagifyApp(CTk):
    def __init__(self):
        super().__init__()
        
        # Set appearance
        set_appearance_mode("dark")
        
        # Window setup
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        self.window_width = int(self.screen_width * 0.8)
        self.window_height = int(self.screen_height * 0.8)
        
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.title("Tagify")
        
        # Initialize frames
        self.home_frame = None
        self.customization_frame = None
        
        # Store data between frames
        self.spotify_data = None
        self.bar_heights = None
        self.model = None
        self.selected_base_model = None
        self.base_model_buttons = []
        self.base_model_paths = []
        
        # Create frames
        self.create_frames()
        self.show_home_page()
    
    def create_frames(self):
        # Create homepage frame
        self.home_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create title
        title = CTkLabel(self.home_frame, text="Tagify", font=("Arial", 48))
        title.place(relx=0.5, rely=0.4, anchor=CENTER)
        
        # Create URL input field
        self.url_input = CTkEntry(
            self.home_frame, 
            placeholder_text="Enter URL", 
            width=(self.window_width // 3),
            height=40,
            corner_radius=12,
            font=("Arial", 14),
            fg_color="gray20",
            text_color="white",
            border_width=2,
            border_color="gray50"
        )
        self.url_input.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Create submit button
        submit_url_btn = CTkButton(
            self.home_frame, 
            text="Submit URL", 
            command=self.process_url
        )
        submit_url_btn.place(relx=0.5, rely=0.55, anchor=CENTER)
        
        # Create developer info
        developer_name = CTkLabel(
            self.home_frame, 
            text="Developed by Sebastian De Leon", 
            font=("Arial", 12), 
            cursor="hand2"
        )
        developer_name.place(relx=0.5, rely=0.8, anchor=CENTER)
        developer_name.bind("<Button-1>", lambda e: utils.open_link("https://sebastiandeleonportfolio.vercel.app/"))
        
        # Create customization frame
        self.customization_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.customization_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid for customization frame to have two columns
        self.customization_frame.grid_columnconfigure(0, weight=1)
        self.customization_frame.grid_columnconfigure(1, weight=1)
        self.customization_frame.grid_rowconfigure(0, weight=1)
        
        # Create left panel (customization options)
        self.left_panel = CTkFrame(self.customization_frame)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add some sample customization options (placeholder)
        options_label = CTkLabel(self.left_panel, text="Customization Options", font=("Arial", 20))
        options_label.pack(pady=20, padx=10)
        
        # --- Base Model Selection ---
        base_models_dir = "./base_models"
        step_files = glob.glob(os.path.join(base_models_dir, "*.step"))
        self.base_model_paths = step_files

        base_model_btn_frame = CTkFrame(self.left_panel, fg_color="transparent")
        base_model_btn_frame.pack(pady=10, padx=10, fill="x")

        self.base_model_buttons = []
        self.selected_base_model = step_files[0] if step_files else None

        def on_base_model_select(idx):
            self.selected_base_model = self.base_model_paths[idx]
            for i, btn in enumerate(self.base_model_buttons):
                btn.configure(border_color="green" if i == idx else "gray50")
            self.update_model_preview()

        for idx, step_path in enumerate(step_files):
            # Try to find a preview image with the same name as the step file
            img_path = os.path.splitext(step_path)[0] + ".png"
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((60, 60))
            else:
                img = Image.new("RGB", (60, 60), color="gray")
            tk_img = CTkImage(light_image=img, dark_image=img, size=(60, 60))
            btn = CTkButton(
                base_model_btn_frame,
                image=tk_img,
                text="",
                width=64,
                height=64,
                fg_color="gray20",
                border_width=3,
                border_color="green" if idx == 0 else "gray50",
                command=lambda i=idx: on_base_model_select(i)
            )
            btn.pack(side="left", padx=5)
            self.base_model_buttons.append(btn)

        # Button to load a custom .step file
        def load_custom_step():
            file_path = filedialog.askopenfilename(
                title="Select STEP file",
                filetypes=[("STEP files", "*.step")]
            )
            if file_path:
                self.selected_base_model = file_path
                for btn in self.base_model_buttons:
                    btn.configure(border_color="gray50")
                self.update_model_preview()

        load_custom_btn = CTkButton(
            base_model_btn_frame,
            text="+",
            width=64,
            height=64,
            fg_color="gray20",
            border_width=3,
            border_color="gray50",
            command=load_custom_step
        )
        load_custom_btn.pack(side="left", padx=5)
        # --- End Base Model Selection ---
        
        # Add an apply button
        generate_btn = CTkButton(
            self.left_panel, 
            text="Generate Model", 
            command=self.export_model
        )
        generate_btn.pack(pady=20, padx=10)
        
        # Add back button
        back_btn = CTkButton(
            self.left_panel, 
            text="Back to Home", 
            command=self.show_home_page
        )
        back_btn.pack(pady=5, padx=10)
        
        # Create right panel (preview)
        self.right_panel = CTkFrame(self.customization_frame)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Add preview label
        preview_label = CTkLabel(self.right_panel, text="Model Preview", font=("Arial", 20))
        preview_label.pack(pady=20)
        
        # The model preview
        self.preview_frame = CTkFrame(self.right_panel, fg_color="gray50")
        self.preview_frame.pack(expand=True, fill="both", pady=10, padx=10)
        

            
        # Configure grid for root window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
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
    
    def generate_model_without_export(self):
        """Generate the model in memory without exporting it."""
        if not self.bar_heights or not self.selected_base_model:
            return None

        try:
            model = cq.importers.importStep(self.selected_base_model)

            # Modify model based on bar heights and customization settings
            curr_bar = 0
            for bar in self.bar_heights:
                model = (
                    model.pushPoints([(15.5 + curr_bar * 1.88, 7.5)])
                    .sketch()
                    .slot(9 / 5 * bar, 1, 90)
                    .finalize()
                    .extrude(4)
                )
                curr_bar += 1

            return model

        except Exception as e:
            print(f"Error generating model: {e}")
            return None
            
    def export_model(self):
            if not self.bar_heights or not self.selected_base_model:
                print("No data to generate model from")
                return
            
            model = cq.importers.importStep(self.selected_base_model)
            
            # Modify model based on bar heights and customization settings
            curr_bar = 0
            for bar in self.bar_heights:
                model = (
                    model.pushPoints([(15.5 + curr_bar * 1.88, 7.5)])
                    .sketch()
                    .slot(9 / 5 * bar, 1, 90)
                    .finalize()
                    .extrude(4)
                )
                curr_bar += 1
            
            # Export model
            cq.exporters.export(model, 'model.stl')
            print("Model exported as model.stl")
            
    def update_model_preview(self):
        """Update the 3D preview in the preview frame."""
        # Clear the preview frame
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Generate the model in memory
        model = self.generate_model_without_export()
        if not model:
            print("No model to preview.")
            return

        # Export the model to a temporary STL file
        temp_stl_path = "temp_preview_model.stl"
        cq.exporters.export(model, temp_stl_path)

        # Use PyVista to render the STL file and save it as an image
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(pv.read(temp_stl_path), color="white")
        plotter.set_background("black")
        temp_image_path = "temp_preview_image.png"
        plotter.screenshot(temp_image_path)
        plotter.close()

        # Display the image in the preview frame using matplotlib
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


if __name__ == "__main__":
    app = TagifyApp()
    app.mainloop()
