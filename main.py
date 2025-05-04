from customtkinter import *

app = CTk()
set_appearance_mode("system")
app.geometry("800x600")
app.title("Tagify")



title = CTkLabel(app, text="Tagify", font=("Arial", 48))
title.place(relx=0.5, rely=0.4, anchor=CENTER)

url_input = CTkEntry(app, placeholder_text="Enter URL")
url_input.place(relx=0.5, rely=0.5, anchor=CENTER)

submit_url_btn = CTkButton(app, text="Submit URL", command=lambda: print(url_input.get()))
submit_url_btn.place(relx=0.5, rely=0.55, anchor=CENTER)

developer_name = CTkLabel(app, text="Developed by Sebastian De Leon", font=("Arial", 12))
developer_name.place(relx=0.5, rely=0.8, anchor=CENTER)

app.mainloop()
