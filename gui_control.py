#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, scrolledtext
import tinytuya
import json

CONFIG_PATH = "/Users/dailuu/Desktop/CT2026/tuya2/config.json"
SNAPSHOT_PATH = "/Users/dailuu/Desktop/CT2026/tuya2/snapshot.json"

def load_devices():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        devices = config.get('IOT_DEVICES', {})
        snapshot_dict = {}
        try:
            with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            for dev in snapshot.get('devices', []):
                snapshot_dict[dev.get('id')] = dev
        except:
            pass
        filtered = {}
        for name, info in devices.items():
            dev_id = info.get('device_id', '')
            ip = info.get('ip_address', '')
            if not ip:
                snap = snapshot_dict.get(dev_id, {})
                ip = snap.get('ip', '')
            if ip and ip.strip() and ip != 'N/A':
                info['ip'] = ip
                ver = info.get('version')
                if not ver:
                    ver = float(snapshot_dict.get(dev_id, {}).get('ver', 3.3))
                info['version'] = ver
                filtered[name] = info
        return filtered
    except Exception as e:
        print(f"Error: {e}")
        return {}

def get_device_type(name, info):
    product = info.get('product_name', '').lower()
    name_lower = name.lower()
    if 'bulb' in product or 'den' in name_lower:
        return 'bulb'
    elif 'socket' in product or 'switch' in product or 'quat' in name_lower:
        return 'outlet'
    return 'outlet'

class TuyaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyTuya Device Control")
        self.root.geometry("750x550")
        self.root.configure(bg='#f0f0f0')
        self.devices = load_devices()

        header = tk.Frame(root, bg='#2c3e50', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="TINYTUYA DEVICE CONTROL",
                font=("Arial", 16, "bold"), fg="white", bg='#2c3e50').pack(pady=15)

        self.status_bar = tk.Label(root, text=f"Found {len(self.devices)} devices with IP",
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#ecf0f1')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not self.devices:
            tk.Label(main_frame, text="No devices with IP found",
                    font=("Arial", 12), fg="red", bg='#f0f0f0').pack(pady=50)
            return

        tk.Label(main_frame, text="Select device to control:",
                font=("Arial", 12, "bold"), bg='#f0f0f0').pack(anchor=tk.W, pady=(0, 10))

        canvas_frame = tk.Frame(main_frame, bg='#f0f0f0')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, (name, info) in enumerate(self.devices.items(), 1):
            device_type = get_device_type(name, info)
            icon = {"bulb": "[B]", "outlet": "[O]", "cover": "[C]"}.get(device_type, "[?]")

            btn_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, bd=1)
            btn_frame.pack(fill=tk.X, pady=5, padx=5)

            info_text = f"{icon} {name}\n"
            info_text += f"   IP: {info['ip']} | Ver: {info.get('version', 'N/A')}\n"
            info_text += f"   Type: {info.get('product_name', 'Unknown')}"

            tk.Label(btn_frame, text=info_text, font=("Arial", 10),
                    justify=tk.LEFT, bg='white', padx=10, pady=10).pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Button(btn_frame, text="Control", font=("Arial", 10, "bold"),
                     bg='#3498db', fg='white', padx=15, pady=5,
                     command=lambda n=name, i=info: self.open_control(n, i)).pack(side=tk.RIGHT, padx=10)

    def open_control(self, name, info):
        device_type = get_device_type(name, info)
        if device_type == 'bulb':
            BulbWindow(self.root, name, info)
        elif device_type == 'outlet':
            OutletWindow(self.root, name, info)

class BulbWindow:
    def __init__(self, parent, name, info):
        self.win = tk.Toplevel(parent)
        self.win.title(f"Control: {name}")
        self.win.geometry("600x750")
        self.win.configure(bg='#f0f0f0')

        self.name = name
        self.info = info
        self.dev_id = info['device_id']
        self.ip = info['ip']
        self.key = info['local_key']
        self.version = info.get('version', 3.3)

        try:
            self.dev = tinytuya.BulbDevice(self.dev_id, self.ip, self.key, version=self.version)
            self.dev.set_socketPersistent(True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect: {e}")
            self.win.destroy()
            return

        header = tk.Frame(self.win, bg='#2980b9', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"[B] {name}", font=("Arial", 14, "bold"),
                fg="white", bg='#2980b9').pack(pady=10)

        status_frame = tk.LabelFrame(self.win, text="Current Status",
                                     font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=4, font=("Courier", 10))
        self.status_text.pack(fill=tk.X)

        btn_frame = tk.Frame(self.win, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="TURN ON", font=("Arial", 11, "bold"),
                 bg='#27ae60', fg='white', padx=20, pady=10,
                 command=self.turn_on).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="TURN OFF", font=("Arial", 11, "bold"),
                 bg='#e74c3c', fg='white', padx=20, pady=10,
                 command=self.turn_off).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Refresh", font=("Arial", 11),
                 bg='#95a5a6', fg='white', padx=20, pady=10,
                 command=self.update_status).grid(row=0, column=2, padx=10)

        color_frame = tk.LabelFrame(self.win, text="Colors",
                                     font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        color_frame.pack(fill=tk.X, padx=20, pady=10)

        colors = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
            ("Orange", (255, 165, 0)),
            ("Purple", (128, 0, 128)),
            ("White", (255, 255, 255)),
        ]

        for i, (cname, rgb) in enumerate(colors):
            fg_c = "black" if cname in ["Yellow", "White", "Green"] else "white"
            btn = tk.Button(color_frame, text=cname, width=10,
                           bg=cname.lower(), fg=fg_c,
                           command=lambda r=rgb: self.set_color(r))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)

        bright_frame = tk.LabelFrame(self.win, text="Brightness (10-1000)",
                                     font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        bright_frame.pack(fill=tk.X, padx=20, pady=10)

        self.b_var = tk.IntVar(value=500)
        self.scale = tk.Scale(bright_frame, from_=10, to=1000, orient=tk.HORIZONTAL,
                                   variable=self.b_var, command=self.set_brightness,
                                   bg='#f0f0f0', length=400)
        self.scale.pack(fill=tk.X)

        mode_frame = tk.LabelFrame(self.win, text="Mode",
                                   font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)

        for i, mode in enumerate(["white", "colour", "scene", "music"]):
            tk.Button(mode_frame, text=mode.capitalize(), width=10,
                     command=lambda m=mode: self.set_mode(m)).grid(row=0, column=i, padx=5, pady=5)

        self.update_status()

    def update_status(self):
        try:
            data = self.dev.status()
            dps = data.get('dps', {})
            text = f"Power: {'ON' if dps.get('20', False) else 'OFF'}\n"
            text += f"Mode: {dps.get('21', 'N/A')}\n"
            text += f"Brightness: {dps.get('22', 'N/A')}\n"
            text += f"Color Temp: {dps.get('23', 'N/A')}"
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, text)
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Error: {e}")

    def turn_on(self):
        try:
            self.dev.turn_on()
            self.update_status()
            messagebox.showinfo("OK", "Turned on")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot turn on: {e}")

    def turn_off(self):
        try:
            self.dev.turn_off()
            self.update_status()
            messagebox.showinfo("OK", "Turned off")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot turn off: {e}")

    def set_color(self, rgb):
        try:
            r, g, b = rgb
            self.dev.set_colour(r, g, b)
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot set color: {e}")

    def set_brightness(self, value):
        try:
            self.dev.set_brightness(int(value))
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot set brightness: {e}")

    def set_mode(self, mode):
        try:
            self.dev.set_mode(mode)
            self.update_status()
            messagebox.showinfo("OK", f"Mode: {mode}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot set mode: {e}")

class OutletWindow:
    def __init__(self, parent, name, info):
        self.win = tk.Toplevel(parent)
        self.win.title(f"Control: {name}")
        self.win.geometry("600x500")
        self.win.configure(bg='#f0f0f0')

        self.name = name
        self.info = info
        self.dev_id = info['device_id']
        self.ip = info['ip']
        self.key = info['local_key']
        self.version = info.get('version', 3.3)

        try:
            self.dev = tinytuya.OutletDevice(self.dev_id, self.ip, self.key, version=self.version)
            self.dev.set_socketPersistent(True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect: {e}")
            self.win.destroy()
            return

        header = tk.Frame(self.win, bg='#16a085', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"[O] {name}", font=("Arial", 14, "bold"),
                fg="white", bg='#16a085').pack(pady=10)

        status_frame = tk.LabelFrame(self.win, text="Switch Status",
                                     font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=4, font=("Courier", 10))
        self.status_text.pack(fill=tk.X)

        switch_frame = tk.LabelFrame(self.win, text="Control Switches",
                                     font=("Arial", 11, "bold"), bg='#f0f0f0', padx=10, pady=10)
        switch_frame.pack(fill=tk.X, padx=20, pady=10)

        self.sw_buttons = {}
        for i, sw in enumerate(['1', '2', '3', '4']):
            btn = tk.Button(switch_frame, text=f"SW{sw}: ...", width=12, height=2,
                           font=("Arial", 10, "bold"),
                           command=lambda s=sw: self.toggle_sw(s))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.sw_buttons[sw] = btn

        master_frame = tk.Frame(self.win, bg='#f0f0f0')
        master_frame.pack(pady=10)

        tk.Button(master_frame, text="TURN ALL ON", font=("Arial", 11, "bold"),
                 bg='#27ae60', fg='white', padx=20, pady=10,
                 command=self.turn_all_on).pack(side=tk.LEFT, padx=10)

        tk.Button(master_frame, text="TURN ALL OFF", font=("Arial", 11, "bold"),
                 bg='#e74c3c', fg='white', padx=20, pady=10,
                 command=self.turn_all_off).pack(side=tk.LEFT, padx=10)

        tk.Button(master_frame, text="Refresh", font=("Arial", 11),
                 bg='#95a5a6', fg='white', padx=20, pady=10,
                 command=self.update_status).pack(side=tk.LEFT, padx=10)

        self.update_status()

    def update_status(self):
        try:
            data = self.dev.status()
            dps = data.get('dps', {})
            text = ""
            for sw in ['1', '2', '3', '4']:
                if sw in dps:
                    state = "ON" if dps[sw] else "OFF"
                    text += f"SW{sw}: {state}\n"
                    color = '#27ae60' if dps[sw] else '#e74c3c'
                    self.sw_buttons[sw].config(text=f"SW{sw}\n{state}", bg=color, fg='white')
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, text if text else "No switches found")
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Error: {e}")

    def toggle_sw(self, sw):
        try:
            data = self.dev.status()
            current = data['dps'].get(sw, False)
            if current:
                self.dev.turn_off(switch=int(sw))
            else:
                self.dev.turn_on(switch=int(sw))
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot toggle SW{sw}: {e}")

    def turn_all_on(self):
        try:
            for sw in ['1', '2', '3', '4']:
                self.dev.turn_on(switch=int(sw))
            self.update_status()
            messagebox.showinfo("OK", "All on")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot turn on: {e}")

    def turn_all_off(self):
        try:
            for sw in ['1', '2', '3', '4']:
                self.dev.turn_off(switch=int(sw))
            self.update_status()
            messagebox.showinfo("OK", "All off")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot turn off: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TuyaGUI(root)
    root.mainloop()
