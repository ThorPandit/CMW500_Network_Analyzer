# UI code
import tkinter as tk
from tkinter import messagebox
import json  # Importing json to handle configuration loading

def run_measurement():
    try:
        # Execute the main measurement script
        exec(open("main_code.py").read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run measurement: {e}")

# Create the main UI window
root = tk.Tk()
root.title("CMW500 LTE Measurement Tool")

# Create a button to run the measurement
run_button = tk.Button(root, text="Run Measurement", command=run_measurement)
run_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
