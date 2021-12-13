# creating the launching desktop application
import tkinter as tk
from tkinter import filedialog, Text
import os
from tkinter.constants import TOP

root = tk.Tk()
root.title("Big Brain - Computer Mouse Control")

def save_file():
    filename = open("filesavetest.txt", 'w')
    filename.write("This is a test. ")
    filename.close()

frame_buttons = tk.Frame(root, width=500, height=800, bg="#285981")
frame_buttons.pack(side=tk.LEFT, fill="both")

frame_streaming = tk.Frame(root, width=900, height=800, bg="#3474A8")
frame_streaming.pack(side=tk.LEFT, fill="both")

button_connect = tk.Button(frame_buttons, text="Connect Headset", width=25, height=5, padx=10, pady=5, fg="white", bg="#28817C",
    font=(18))
button_connect.pack()

button_control_cursor = tk.Button(frame_buttons, text="Control Cursor", width=25, height=5, padx=10, pady=5, fg="white", bg="#28817C",
    font=(18))
button_control_cursor.pack()

button_save = tk.Button(frame_buttons, text="Save Data", width=25, height=5, padx=10, pady=5, fg="white", bg="#28817C",
    font=(18))
button_save.pack()

button_tutorial = tk.Button(frame_buttons, text="Tutorial", width=25, height=5, padx=10, pady=5, fg="white", bg="#28817C",
    font=(18))
button_tutorial.pack()

button_settings = tk.Button(frame_buttons, text="Settings", width=25, height=5, padx=10, pady=5, fg="white", bg="#28817C",
    font=(18))
button_settings.pack()

root.mainloop()