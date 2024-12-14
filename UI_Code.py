import tkinter as tk
from tkinter import messagebox, filedialog
import json
import threading
import main_code
import matplotlib.pyplot as plt
import csv

# Load configuration
def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {
            "device_address": "",
            "bands": [],
            "power_levels": [],
            "max_retries": 5,
            "timeout": 30000
        }

# Save configuration
def save_config():
    config = {
        "device_address": device_address_entry.get(),
        "bands": [band for band, var in bands_var.items() if var.get()],
        "power_levels": [level.strip() for level in power_entry.get().split(",")],
        "max_retries": int(retry_entry.get()),
        "timeout": int(timeout_entry.get())
    }
    try:
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

# Run measurement
def run_measurement():
    try:
        save_config()
        messagebox.showinfo("Info", "Starting measurements...")
        main_code.run_measurements()  # Call a function in main_code
        messagebox.showinfo("Success", "Measurements completed successfully!")
        #exec(open("main_code.py").read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run measurement: {e}")

def show_graph():
    try:
        import csv
        import matplotlib.pyplot as plt

        results = []
        with open("network_measurements.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Preprocess and convert values
                rsrp = float(row["RSRP"]) if float(row["RSRP"]) < 0 else -abs(float(row["RSRP"]))
                rsrq = float(row["RSRQ"]) if float(row["RSRQ"]) < 0 else -abs(float(row["RSRQ"]))
                results.append({
                    "band": row["band"],
                    "power_level": row["power_level"],
                    "RSRP": rsrp,
                    "RSRQ": rsrq,
                })

        if not results:
            raise ValueError("No data available in the CSV file.")

        # Group data by power levels
        data_by_power = {}
        for result in results:
            power = result["power_level"]
            if power not in data_by_power:
                data_by_power[power] = []
            data_by_power[power].append(result)

        # Plotting
        plt.figure(figsize=(12, 6))
        markers = ["o", "s"]  # Different markers for RSRP and RSRQ
        for i, power_level in enumerate(sorted(data_by_power.keys())):
            power_data = data_by_power[power_level]
            bands = [entry["band"] for entry in power_data]
            rsrp_values = [entry["RSRP"] for entry in power_data]
            rsrq_values = [entry["RSRQ"] for entry in power_data]

            # Plot RSRP
            plt.plot(
                bands,
                rsrp_values,
                label=f"RSRP (Power {power_level} dBm)",
                marker=markers[0],
                linestyle="-",
            )

            # Plot RSRQ
            plt.plot(
                bands,
                rsrq_values,
                label=f"RSRQ (Power {power_level} dBm)",
                marker=markers[1],
                linestyle="--",
            )

        plt.title("RSRP and RSRQ Across Bands for Different Power Levels")
        plt.xlabel("Bands")
        plt.ylabel("Signal Quality (dBm/dB)")
        plt.axhline(y=0, color="red", linestyle="--", label="Reference Line (0 dB)")
        plt.legend(loc="best")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        messagebox.showerror("Error", "No results file found. Please run a measurement first.")
    except KeyError as e:
        messagebox.showerror("Error", f"Missing column in CSV file: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"No data available for graphing: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display graph: {e}")

# Main UI
root = tk.Tk()
root.title("CMW500 LTE Measurement Tool")

# Device Address
device_address_label = tk.Label(root, text="Device Address:")
device_address_label.pack()
device_address_entry = tk.Entry(root, width=30)
device_address_entry.pack()

# Band Selection
bands_label = tk.Label(root, text="Select Bands:")
bands_label.pack()
bands_var = {}
for band in ["OB1","OB3","OB5","OB8","OB20","OB40"]:  # Add more bands as needed
    var = tk.BooleanVar()
    bands_var[band] = var
    checkbox = tk.Checkbutton(root, text=band, variable=var)
    checkbox.pack(anchor="w")

# Power Levels
power_label = tk.Label(root, text="Enter Power Levels (comma-separated):")
power_label.pack()
power_entry = tk.Entry(root)
power_entry.pack()

# Retry Attempts
retry_label = tk.Label(root, text="Retry Attempts:")
retry_label.pack()
retry_entry = tk.Entry(root)
retry_entry.pack()

# Timeout
timeout_label = tk.Label(root, text="Timeout (ms):")
timeout_label.pack()
timeout_entry = tk.Entry(root)
timeout_entry.pack()

# Buttons
save_button = tk.Button(root, text="Save Configuration", command=save_config)
save_button.pack(pady=5)

run_button = tk.Button(root, text="Run Measurement", command=lambda: threading.Thread(target=run_measurement).start())
run_button.pack(pady=5)

graph_button = tk.Button(root, text="View Graph", command=show_graph)
graph_button.pack(pady=5)

root.mainloop()
