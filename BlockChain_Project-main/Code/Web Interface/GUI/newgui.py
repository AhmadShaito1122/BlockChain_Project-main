import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import subprocess
import re
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import platform
from collections import defaultdict

# Paths to JS files
MINER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/miner.js"
MANUFACTURER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/manufacturer.js"
LATEST_FIRMWARE_VERSION = "v1.2.3"

# Global variables
graph_frame = None
canvas = None
output_frame = None
output_text = None
graph_active = False
monitor_thread = None
miner_process = None
device_status = defaultdict(dict)
output_buffer = ""

#Adding Device 
def add_device(ip):
    try:
        #  Update miner.js (existing code)
        with open(MINER_JS_PATH, "r") as file:
            miner_content = file.read()

        match = re.search(r"(let\s+device_array\s*=\s*\[)([^\]]*)(\];)", miner_content)
        if not match:
            messagebox.showerror("Error", "device_array not found in miner.js")
            return

        current_ips = [ip.strip().strip("'\"") for ip in match.group(2).split(',') if ip.strip()]
        if ip in current_ips:
            messagebox.showinfo("Info", "IP already exists.")
            return

        current_ips.append(ip)
        new_array = match.group(1) + ", ".join(f"'{x}'" for x in current_ips) + match.group(3)
        new_miner_content = miner_content[:match.start()] + new_array + miner_content[match.end():]

        with open(MINER_JS_PATH, "w") as file:
            file.write(new_miner_content)

        #  Update minerInput.py
        MINER_INPUT_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/minerInput.py"
        
        with open(MINER_INPUT_PATH, "r") as file:
            miner_input_content = file.read()

        # Find and update device_links array
        device_links_match = re.search(r"(device_links\s*=\s*\[)([^\]]*)(\])", miner_input_content)
        if device_links_match:
            current_links = [link.strip().strip('"\'') for link in device_links_match.group(2).split(',') if link.strip()]
            new_link = f"http://{ip}:8080"
            
            if new_link in current_links:
                messagebox.showinfo("Info", "IP already exists in minerInput.py")
            else:
                current_links.append(new_link)
                new_links_array = device_links_match.group(1) + ", ".join(f'"{x}"' for x in current_links) + device_links_match.group(3)
                new_miner_input_content = miner_input_content[:device_links_match.start()] + new_links_array + miner_input_content[device_links_match.end():]
                
                with open(MINER_INPUT_PATH, "w") as file:
                    file.write(new_miner_input_content)
        else:
            # If device_links doesn't exist, create it
            new_miner_input_content = miner_input_content + f"\ndevice_links = [\"http://{ip}:8080\"]\n"
            with open(MINER_INPUT_PATH, "w") as file:
                file.write(new_miner_input_content)

        messagebox.showinfo("Success", f"IP {ip} added to both miner.js and minerInput.py")
        update_device_list()
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to remove selected device from miner.js
def remove_selected_device():
    selected = device_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a device to remove.")
        return

    selected_ip = device_listbox.get(selected[0])

    try:
        # 1. Remove from miner.js
        with open(MINER_JS_PATH, "r+") as file:
            content = file.read()
            match = re.search(r"(let\s+device_array\s*=\s*\[)([^\]]*)(\];)", content)
            if not match:
                messagebox.showerror("Error", "device_array not found in miner.js")
                return

            current_ips = [ip.strip().strip("'\"") for ip in match.group(2).split(',') if ip.strip()]
            if selected_ip not in current_ips:
                messagebox.showerror("Error", f"{selected_ip} not found in device_array.")
                return

            current_ips.remove(selected_ip)
            new_content = content[:match.start()] + match.group(1) + ", ".join(f"'{x}'" for x in current_ips) + match.group(3) + content[match.end():]
            file.seek(0)
            file.write(new_content)
            file.truncate()

        # 2. Remove from minerInput.py
        MINER_INPUT_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/minerInput.py"
        
        with open(MINER_INPUT_PATH, "r+") as file:
            content = file.read()
            device_links_match = re.search(r"(device_links\s*=\s*\[)([^\]]*)(\])", content)
            
            if device_links_match:
                current_links = [link.strip().strip('"\'') for link in device_links_match.group(2).split(',') if link.strip()]
                url_to_remove = f"http://{selected_ip}:8080"
                
                if url_to_remove in current_links:
                    current_links.remove(url_to_remove)
                    new_content = content[:device_links_match.start()] + device_links_match.group(1) + ", ".join(f'"{x}"' for x in current_links) + device_links_match.group(3) + content[device_links_match.end():]
                    file.seek(0)
                    file.write(new_content)
                    file.truncate()
                else:
                    messagebox.showinfo("Info", f"URL {url_to_remove} not found in minerInput.py")
            else:
                messagebox.showinfo("Info", "device_links array not found in minerInput.py")

        messagebox.showinfo("Success", f"Device {selected_ip} removed from both files")
        update_device_list()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove device:\n{str(e)}")

FIRMWARE_LOG_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/firmware_log.txt"
LATEST_FIRMWARE_VERSION = "v1.2.3"  # Replace with your real latest version



# Function to run all scripts
def run_all():
    try:
        subprocess.run(["node", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/unlock.js"])
        subprocess.Popen(["node", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/miner.js"])
        subprocess.Popen(["python3", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/minerInput.py"])
        subprocess.Popen(["node", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/manufacturer.js"])
        messagebox.showinfo("Running", "All scripts have been started.")
    except Exception as e:
        messagebox.showerror("Execution Failed", str(e))

# Function to upload and replace .hex file path
def upload_hex_file():
    global hex_file_path
    hex_file_path = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
    if not hex_file_path:
        return

    try:
        # Backup old manufacturer.js
        shutil.copy(MANUFACTURER_JS_PATH, MANUFACTURER_JS_PATH + ".bak")

        with open(MANUFACTURER_JS_PATH, 'r') as f:
            content = f.read()

        # Only replace the firmware `.hex` file path
        new_path = hex_file_path.replace("\\", "/")  # Ensure path is safe for JS
        pattern = (
            r"(const\s+message\s*=\s*fs\.readFileSync\(\s*')[^']+('\s*,\s*'utf-8'\s*\)\.replace\(/\\s\+/g,\s*''\);)"
        )

        # Perform the safe replacement
        new_content = re.sub(pattern, rf"\1{new_path}\2", content)

        with open(MANUFACTURER_JS_PATH, 'w') as f:
            f.write(new_content)

        messagebox.showinfo("Upload Successful", f"HEX file uploaded:\n{hex_file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update manufacturer.js\n{e}")


# Function to extract and update the device list in the listbox
def update_device_list():
    try:
        with open(MINER_JS_PATH, "r") as file:
            content = file.read()

        match = re.search(r"let\s+device_array\s*=\s*\[([^\]]*)\];", content)
        if not match:
            device_listbox.delete(0, tk.END)
            device_listbox.insert(tk.END, "No device_array found.")
            return

        ips = [ip.strip().strip("'\"") for ip in match.group(1).split(',') if ip.strip()]
        device_listbox.delete(0, tk.END)
        for ip in ips:
            device_listbox.insert(tk.END, ip)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_all():
    global miner_process, output_text
    
    try:
        # Stop any existing miner process
        if miner_process:
            miner_process.terminate()
            miner_process = None
        
        # Clear output text
        if output_text:
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.config(state=tk.DISABLED)
        
        subprocess.run(["node", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/unlock.js"])
        miner_process = subprocess.Popen(
            ["node", MINER_JS_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        subprocess.Popen(["python3", "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/minerInput.py"])
        subprocess.Popen(["node", MANUFACTURER_JS_PATH])
        messagebox.showinfo("Running", "All scripts have been started.")
        
        # Start monitoring output if not already running
        if not graph_active:
            start_monitoring()
    except Exception as e:
        messagebox.showerror("Execution Failed", str(e))

def monitor_miner_output():
    global graph_active, output_buffer, output_text
    
    while graph_active and miner_process:
        # Read output character by character
        char = miner_process.stdout.read(1)
        if not char:
            time.sleep(0.1)
            continue
        
        output_buffer += char
        
        # Process complete lines
        if '\n' in output_buffer:
            line, output_buffer = output_buffer.split('\n', 1)
            line = line.strip()
            
            # Display the output in the text widget
            if output_text and line:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, line + "\n")
                output_text.see(tk.END)
                output_text.config(state=tk.DISABLED)
            
            # Process for firmware information
            process_miner_line(line)
            
        # Update graph periodically
        if time.time() % 5 < 0.1:  # About every 5 seconds
            update_graph_from_status()

def process_miner_line(line):
    global device_status
    
    try:
        # Check for device firmware messages
        if "Device" in line and "firmware:" in line:
            match = re.search(r"Device (\d+) firmware: ([a-f0-9]+)", line)
            if match:
                device_num = int(match.group(1))
                firmware = match.group(2)
                device_status[device_num]['firmware'] = firmware
                device_status[device_num]['status'] = 'outdated'
                
        elif "Device firmware up to date!" in line:
            match = re.search(r"Device (\d+)", line)
            if match:
                device_num = int(match.group(1))
                device_status[device_num]['status'] = 'up_to_date'
                
        elif "Manufacturer signature verified" in line or "Latest firmware saved" in line:
            # These are important status messages we might want to highlight
            pass
            
    except Exception as e:
        print(f"Error processing line: {e}")

def update_graph_from_status():
    global device_status
    
    updated = 0
    outdated = 0
    
    for device in device_status.values():
        if device.get('status') == 'up_to_date':
            updated += 1
        else:
            outdated += 1
    
    update_graph(updated, outdated)

def update_graph(updated, outdated):
    global canvas
    
    # Clear previous graph
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    # Create new figure
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    # Data for plotting
    labels = ['Up to date', 'Outdated']
    sizes = [updated, outdated]
    colors = ['#4CAF50', '#F44336']
    
    # Create pie chart only if we have data
    if sum(sizes) > 0:
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title(f'Device Firmware Status (Total: {sum(sizes)})')
    else:
        ax.text(0.5, 0.5, 'Waiting for data...\nRun scripts and start monitoring', 
               ha='center', va='center')
        ax.set_title('Device Firmware Status')
    
    ax.axis('equal')
    
    # Create canvas and add to frame
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def start_monitoring():
    global graph_active, monitor_thread
    
    if not miner_process:
        messagebox.showwarning("Warning", "Please run the scripts first")
        return
        
    if not graph_active:
        graph_active = True
        monitor_thread = threading.Thread(target=monitor_miner_output, daemon=True)
        monitor_thread.start()
        messagebox.showinfo("Info", "Started monitoring device firmware status")
        update_graph_from_status()

def stop_monitoring():
    global graph_active
    
    if graph_active:
        graph_active = False
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread.join(timeout=1)
        messagebox.showinfo("Info", "Stopped monitoring device firmware status")

# GUI setup
def setup_gui():
    global root, device_listbox, graph_frame, output_frame, output_text
    
    root = tk.Tk()
    root.title("Blockchain IoT Device Manager")
    root.geometry("1200x700")
    root.configure(bg="#f0f2f5")

    # Left Sidebar
    sidebar = tk.Frame(root, width=300, bg="#ffffff", bd=2, relief="groove")
    sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Add Device Section
    add_frame = tk.LabelFrame(sidebar, text="Add New Device", bg="#ffffff", padx=10, pady=10)
    add_frame.pack(fill=tk.X, pady=10)

    tk.Label(add_frame, text="Device IP:", bg="#ffffff").pack(anchor="w")
    ip_entry = tk.Entry(add_frame, width=30)
    ip_entry.pack(pady=5)
    tk.Button(add_frame, text="➕ Add Device", command=lambda: add_device(ip_entry.get()), bg="#4CAF50", fg="white").pack(pady=5)

    # Device Management Section
    device_frame = tk.LabelFrame(sidebar, text="Device Dashboard", bg="#ffffff", padx=10, pady=10)
    device_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    scrollbar = tk.Scrollbar(device_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    device_listbox = tk.Listbox(device_frame, height=8, width=30, yscrollcommand=scrollbar.set)
    device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=device_listbox.yview)

    btns = tk.Frame(device_frame, bg="#ffffff")
    btns.pack(fill=tk.X, pady=5)
    tk.Button(btns, text="🔄 Refresh List", command=update_device_list).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(btns, text="🗑 Remove", command=remove_selected_device, fg="red").pack(side=tk.LEFT, expand=True, padx=5)

    # Script & Firmware Section
    scripts_frame = tk.LabelFrame(sidebar, text="Firmware & Scripts", bg="#ffffff", padx=10, pady=10)
    scripts_frame.pack(fill=tk.X, pady=10)

    tk.Button(scripts_frame, text="⬆ Upload .hex File", command=upload_hex_file).pack(fill=tk.X, pady=5)
    tk.Button(scripts_frame, text="▶ Run All Scripts", command=run_all, bg="#2196F3", fg="white").pack(fill=tk.X, pady=5)

    # Monitoring Controls
    monitor_frame = tk.LabelFrame(sidebar, text="Monitoring", bg="#ffffff", padx=10, pady=10)
    monitor_frame.pack(fill=tk.X, pady=10)

    tk.Button(monitor_frame, text="🟢 Start Monitoring", command=start_monitoring).pack(fill=tk.X, pady=2)
    tk.Button(monitor_frame, text="🔴 Stop Monitoring", command=stop_monitoring).pack(fill=tk.X, pady=2)

    # Right Main Panel
    main_panel = tk.Frame(root, bg="#f0f2f5")
    main_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Output Console
    output_frame = tk.LabelFrame(main_panel, text="Miner Output Log", bg="#ffffff", padx=5, pady=5)
    output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#eeeeee", font=("Courier", 10))
    output_text.pack(fill=tk.BOTH, expand=True)

    # Graph Section
    graph_frame = tk.LabelFrame(main_panel, text="Device Firmware Status", bg="#ffffff", padx=5, pady=5)
    graph_frame.pack(fill=tk.BOTH, expand=True)

    update_graph(0, 0)
    update_device_list()

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
    graph_active = False