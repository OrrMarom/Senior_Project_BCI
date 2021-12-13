# Senior_Project_BCI

Our application is focused on using a EEG headset to control a computer's cursor and trigger mental shortcuts. The goal is to allow the user to interact with the computer solely using the headset. While this application can be used by anyone with a supported headset, it is aimed towards people with disabilities who have difficulty using regular computer equipment.

## Hardware
We are using the **OpenBCI Ganglion** board with 4 channels.

## Software
To interact with the board we are primarily using the Brainflow library. The library supports several popular EEG headsets, among which is the OpenBCI Ganglion board.
The library allows us to stream data from the board in realtime. It also has APIs for signal processing and ML models.

To assist with processing the data we are also using Numpy and Pandas

To control the device's cursor/keyboard we are using PyAutoGUI

To create our GUI we are using Python Tkinter

## User Requirements
- User shall be able to connect the headset to the software.
- User shall be able to maneuver over the GUI easily. 
- User shall be able to control the mouse cursor.
- User shall be able to save data.
- User shall be able to create shortcuts.
- User shall be able to train with BCI.

## System Requirements
- Software shall output live EEG data.
- Software shall be able to connect to the OpenBCI headset.
- Software shall mimic a mouse click by some metric.
- Software shall be able re-run saved data (shortcuts).
