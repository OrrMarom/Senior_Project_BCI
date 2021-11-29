# creating the launching desktop application
import tkinter as tk
from tkinter import filedialog, Text
import os

root = tk.Tk()
root.title("Big Brain - Computer Mouse Control")

def save_file():
    filename = open("filesavetest.txt", 'w')
    filename.write("This is a test. ")
    filename.close()

frame_buttons = tk.Frame(master=root, width=500, height=800, bg="#285981")
frame_buttons.pack(side=tk.LEFT, fill="both")

frame_streaming = tk.Frame(master=root, width=900, height=800, bg="#3474A8")
frame_streaming.pack(side=tk.LEFT, fill="both")


button_connect = tk.Button(frame_buttons, text="Connect Headset", padx=10, pady=5, fg="white", bg="#28817C")
button_connect.pack(pady=20, padx=20)

button_control_cursor = tk.Button(frame_buttons, text="Control Cursor", padx=10, pady=5, fg="white", bg="#28817C")
button_control_cursor.pack(pady=20, padx=20)

button_save = tk.Button(frame_buttons, text="Save Data", padx=10, pady=5, fg="white", bg="#28817C")
button_save.pack(pady=20, padx=20)

button_tutorial = tk.Button(frame_buttons, text="Tutorial", padx=10, pady=5, fg="white", bg="#28817C")
button_tutorial.pack(pady=20, padx=20)

button_settings = tk.Button(frame_buttons, text="Settings", padx=10, pady=5, fg="white", bg="#28817C")
button_settings.pack(pady=20, padx=20)

root.mainloop()