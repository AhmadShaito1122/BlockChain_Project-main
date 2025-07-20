import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import re
import os

# Paths to JS files
MINER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/miner.js"
MANUFACTURER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/manufacturer.js"

# Function to add a device IP to miner.js
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import re
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import platform
from collections import defaultdict

# Constants
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4a6fa5"
TEXT_COLOR = "#333333"
ACCENT_COLOR = "#166088"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

# Paths
MINER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/miner.js"
MANUFACTURER_JS_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/manufacturer.js"
MINER_INPUT_PATH = "/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/Code/minerInput.py"
LATEST_FIRMWARE_VERSION = "v1.2.3"

# Global variables
root = None
device_listbox = None
graph_frame = None
output_text = None
canvas = None
graph_active = False
monitor_thread = None
miner_process = None
device_status = defaultdict(dict)
output_buffer = ""

def setup_gui():
    global root, device_listbox, graph_frame, output_text, canvas
    
    root = tk.Tk()
    root.title("IoT Device Manager")
    root.configure(bg=BG_COLOR)
    
    # Set window size and position
    window_width = 1100
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    
    # Create main container
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Left panel - Controls
    left_panel = ttk.LabelFrame(main_frame, text="Device Management", padding=10)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    # IP Entry Section
    ip_frame = ttk.Frame(left_panel)
    ip_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(ip_frame, text="Device IP Address:").pack(side=tk.LEFT)
    ip_entry = ttk.Entry(ip_frame, width=20)
    ip_entry.pack(side=tk.LEFT, padx=5)
    
    add_btn = ttk.Button(left_panel, text="Add Device", 
                        command=lambda: add_device(ip_entry.get()),
                        style="Accent.TButton")
    add_btn.pack(fill=tk.X, pady=5)
    
    # Device List
    ttk.Label(left_panel, text="Connected Devices:").pack(pady=(10,0))
    
    list_frame = ttk.Frame(left_panel)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    device_listbox = tk.Listbox(list_frame, 
                              yscrollcommand=scrollbar.set,
                              bg="white",
                              fg=TEXT_COLOR,
                              selectbackground=ACCENT_COLOR,
                              font=FONT)
    device_listbox.pack(fill=tk.BOTH, expand=True)
    
    scrollbar.config(command=device_listbox.yview)
    
    btn_frame = ttk.Frame(left_panel)
    btn_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(btn_frame, text="Remove Selected", 
              command=remove_selected_device).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Refresh List", 
              command=update_device_list).pack(side=tk.RIGHT, padx=2)
    
    # File Operations
    file_frame = ttk.LabelFrame(left_panel, text="File Operations", padding=10)
    file_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(file_frame, text="Upload .hex File", 
              command=upload_hex_file).pack(fill=tk.X, pady=2)
    
    # Right panel - Output and Monitoring
    right_panel = ttk.Frame(main_frame)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Output Console
    output_frame = ttk.LabelFrame(right_panel, text="System Output", padding=10)
    output_frame.pack(fill=tk.BOTH, expand=True)
    
    output_text = scrolledtext.ScrolledText(output_frame, 
                                          wrap=tk.WORD,
                                          bg="white",
                                          fg=TEXT_COLOR,
                                          font=FONT)
    output_text.pack(fill=tk.BOTH, expand=True)
    output_text.config(state=tk.DISABLED)
    
    # Graph and Monitoring
    graph_frame = ttk.LabelFrame(right_panel, text="Firmware Status", padding=10)
    graph_frame.pack(fill=tk.BOTH, expand=True)
    
    # Monitoring Controls
    monitor_frame = ttk.Frame(right_panel)
    monitor_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(monitor_frame, text="Run All Scripts", 
              command=run_all,
              style="Accent.TButton").pack(side=tk.LEFT, padx=2)
    
    ttk.Button(monitor_frame, text="Start Monitoring", 
              command=start_monitoring).pack(side=tk.LEFT, padx=2)
    ttk.Button(monitor_frame, text="Stop Monitoring", 
              command=stop_monitoring).pack(side=tk.LEFT, padx=2)
    
    # Status Bar
    status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)
    
    # Configure styles
    style = ttk.Style()
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, font=FONT)
    style.configure("TButton", font=FONT, padding=5)
    style.configure("Accent.TButton", background=BUTTON_COLOR, foreground="white")
    style.configure("TLabelFrame", background=BG_COLOR)
    style.configure("TEntry", font=FONT)
    
    # Initial setup
    update_graph(0, 0)
    update_device_list()
    
    root.mainloop()

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
        update_status(f"Removing device {selected_ip}...")
        log_output(f"Starting removal of device {selected_ip}")

        # 1. Remove from miner.js
        with open(MINER_JS_PATH, "r+") as file:
            content = file.read()
            match = re.search(r"(let\s+device_array\s*=\s*\[)([^\]]*)(\];)", content)
            if not match:
                raise ValueError("device_array not found in miner.js")

            current_ips = [ip.strip().strip("'\"") for ip in match.group(2).split(',') if ip.strip()]
            if selected_ip not in current_ips:
                messagebox.showinfo("Info", f"{selected_ip} not found in miner.js")
                return

            current_ips.remove(selected_ip)
            new_content = content[:match.start()] + match.group(1) + ", ".join(f"'{x}'" for x in current_ips) + match.group(3) + content[match.end():]
            file.seek(0)
            file.write(new_content)
            file.truncate()

        log_output(f"Removed {selected_ip} from miner.js")

        # 2. Remove from minerInput.py
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
                    log_output(f"Removed {url_to_remove} from minerInput.py")
                else:
                    log_output(f"{url_to_remove} not found in minerInput.py")

        update_status(f"Successfully removed {selected_ip}")
        messagebox.showinfo("Success", f"Device {selected_ip} removed from both files")
        update_device_list()

    except Exception as e:
        update_status("Error removing device")
        log_output(f"ERROR: {str(e)}")
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
    file_path = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
    if not file_path:
        return

    try:
        with open(MANUFACTURER_JS_PATH, "r") as file:
            content = file.read()

        new_path = file_path.replace("\\", "/")
        new_content = re.sub(
            r"(fs\.readFileSync\(\s*')[^']+('\s*,\s*'utf-8'\s*\))",
            rf"\1{new_path}\2",
            content
        )

        with open(MANUFACTURER_JS_PATH, "w") as file:
            file.write(new_content)

        messagebox.showinfo("Success", f".hex file path updated:\n{new_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

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

def log_output(message):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, message + "\n")
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)

def update_status(message):
    root.status_bar.config(text=message)
    root.update_idletasks()

# Example modified add_device with UI feedback:
def add_device(ip):
    if not ip:
        messagebox.showwarning("Input Error", "Please enter an IP address")
        return
    
    try:
        # Validate IP format
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            messagebox.showerror("Input Error", "Invalid IP address format")
            return
        
        update_status(f"Adding device {ip}...")
        log_output(f"Attempting to add device: {ip}")
        
        # Rest of your existing add_device implementation
        # ...
        
        update_status(f"Successfully added device {ip}")
        log_output(f"Device {ip} added successfully")
        
    except Exception as e:
        update_status("Error adding device")
        log_output(f"Error: {str(e)}")
        messagebox.showerror("Error", str(e))

# [Rest of your functions with similar UI feedback additions]

if __name__ == "__main__":
    setup_gui()
    graph_active = False
# GUI setup
import platform

root = tk.Tk()
root.title("Device Manager GUI")

# Maximize window depending on platform
if platform.system() == "Windows":
    root.state('zoomed')  # Windows-specific maximize
else:
    root.attributes("-zoomed", True)  # Linux/Gnome/others

root.resizable(True, True)


# IP Entry Section
tk.Label(root, text="Enter new device IP:").pack(pady=5)
ip_entry = tk.Entry(root, width=35)
ip_entry.pack(pady=5)

tk.Button(root, text="Add Device", command=lambda: add_device(ip_entry.get())).pack(pady=5)
tk.Button(root, text="Upload .hex File", command=upload_hex_file).pack(pady=5)
tk.Button(root, text="Run All Scripts", command=run_all).pack(pady=10)

# Device Dashboard
tk.Label(root, text="Device Dashboard (device_array):").pack(pady=5)
frame = tk.Frame(root)
frame.pack(pady=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

device_listbox = tk.Listbox(frame, height=8, width=60, yscrollcommand=scrollbar.set)
device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=device_listbox.yview)

tk.Button(root, text="Update Device List", command=update_device_list).pack(pady=5)
tk.Button(root, text="Remove Selected Device", command=remove_selected_device).pack(pady=5)

# Load device list initially
update_device_list()

root.mainloop()
