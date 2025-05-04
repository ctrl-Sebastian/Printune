from customtkinter import *

import cadquery as cq
import requests
import io
from PIL import Image
import utils

app = CTk()
set_appearance_mode("dark")
app.geometry("800x600")     
app.title("Tagify")

def submit_url():
    URL = "https://www.spotifycodes.com/downloadCode.php?uri=jpeg%2F000000%2Fwhite%2F640%2Fspotify%3Aalbum%3A4m2880jivSbbyEGAKfITCa"
    
    # GET INPUT URL
    share_link = url_input.get()

    data = utils.get_link_data(share_link)

    if len(data) != 2:
        print("Something went wrong while parsing the URL.")
        exit(-1)


    # DOWNLOAD SPOTIFY CODE SVG
    code_URL = "https://www.spotifycodes.com/downloadCode.php?uri=jpeg%2F000000%2Fwhite%2F640%2Fspotify%3A" + data[0] + "%3A" + data[1]

    r = requests.get(code_URL)

    if not r.ok or not r.content:
        print("Something went wrong while fetching the Spotify code.")
        exit(-1)


    # LOADING SVG
    img = Image.open(io.BytesIO(r.content)).crop((160,0, 640-31, 160))
    width, height = img.size

    pix = img.load()


    # GETTING BAR LENGTHS
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

    print(f"There are {len(bar_heights)} bars of heights {bar_heights}")


    # EXTRUDING FROM BASE MODEL
    model = cq.importers.importStep('base_model.step')

    curr_bar = 0

    for bar in bar_heights:
        model = (
            model.pushPoints([(15.5 + curr_bar * 1.88, 7.5)])
            .sketch()
            .slot(9 / 5 * bar, 1, 90)
            .finalize()
            .extrude(4)
        )
        curr_bar += 1

    cq.exporters.export(model, 'model.stl')
    print("Model exported as model.stl")
    url_input.delete(0, 'end')

title = CTkLabel(app, text="Tagify", font=("Arial", 48))
title.place(relx=0.5, rely=0.4, anchor=CENTER)

url_input = CTkEntry(app, placeholder_text="Enter URL")
url_input.place(relx=0.5, rely=0.5, anchor=CENTER)

submit_url_btn = CTkButton(app, text="Submit URL", command=submit_url)
submit_url_btn.place(relx=0.5, rely=0.55, anchor=CENTER)

developer_name = CTkLabel(app, text="Developed by Sebastian De Leon", font=("Arial", 12))
developer_name.place(relx=0.5, rely=0.8, anchor=CENTER)


app.mainloop()
