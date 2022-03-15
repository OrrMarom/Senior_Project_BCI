# 3/15/22 Tkinter does not play nice with PyQt5, switching to PyQt5 for GUI purposes
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
#button 

frame_streaming = tk.Frame(root, width=900, height=800, bg="#3474A8")
frame_streaming.pack(side=tk.LEFT, fill="both")
#button 

frame_s_graph = tk.Frame(frame_streaming, width=800, height=300, bg="green")
frame_s_graph.pack(pady=30, padx=30)
#button 

frame_s_short = tk.Frame(frame_streaming, width=800, height=300, bg="blue")
frame_s_short.pack(pady=30, padx=30)
#button 

#frame_s_short_title = tk.Frame(frame_s_short, width=800, height=50, bg="white")
#frame_s_short_title.pack()
#frame_s_short_title.pack()
#
#
#
#
#
#
#
#
#
#
#
#

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
