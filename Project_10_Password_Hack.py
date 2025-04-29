import itertools
import string
import time
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import json
import threading


class WiFiCrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Password Cracker")
        self.root.geometry("700x500")

        # Variables
        self.scanning = False
        self.attacking = False
        self.stop_attack = False

        self.setup_ui()

    def setup_ui(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Brute Force Tab
        self.bf_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bf_tab, text="Brute Force Attack")
        self.setup_brute_force_tab()

        # WiFi Scanner Tab
        self.wifi_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.wifi_tab, text="WiFi Scanner")
        self.setup_wifi_tab()

    def setup_brute_force_tab(self):
        # Target Password Frame
        target_frame = ttk.LabelFrame(self.bf_tab, text="Target Password")
        target_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(target_frame, text="Enter Password:").pack(side='left', padx=5)
        self.password_entry = ttk.Entry(target_frame, width=30)
        self.password_entry.pack(side='left', padx=5)

        ttk.Button(target_frame, text="Start Attack", command=self.start_brute_force).pack(side='right', padx=5)

        # Options Frame
        options_frame = ttk.LabelFrame(self.bf_tab, text="Options")
        options_frame.pack(pady=5, padx=10, fill='x')

        ttk.Label(options_frame, text="Max Length:").grid(row=0, column=0, padx=5, sticky='e')
        self.max_len_bf = ttk.Combobox(options_frame, values=list(range(1, 13)), width=5)
        self.max_len_bf.current(7)  # Default to 8
        self.max_len_bf.grid(row=0, column=1, padx=5, sticky='w')

        # Results Frame
        results_frame = ttk.LabelFrame(self.bf_tab, text="Results")
        results_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.results_text = tk.Text(results_frame, height=10, wrap='word')
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text.config(yscrollcommand=scrollbar.set)

    def setup_wifi_tab(self):
        # WiFi Scan Frame
        scan_frame = ttk.LabelFrame(self.wifi_tab, text="Available Networks")
        scan_frame.pack(pady=10, padx=10, fill='x')

        # Treeview for networks
        self.wifi_tree = ttk.Treeview(scan_frame, columns=('SSID', 'Signal', 'Security'), show='headings')
        self.wifi_tree.heading('SSID', text='Network Name')
        self.wifi_tree.heading('Signal', text='Signal Strength')
        self.wifi_tree.heading('Security', text='Security Type')
        self.wifi_tree.column('SSID', width=200)
        self.wifi_tree.column('Signal', width=100)
        self.wifi_tree.column('Security', width=150)
        self.wifi_tree.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Button(scan_frame, text="Scan Networks", command=self.start_scan_thread).pack(pady=5)

        # Attack Frame
        attack_frame = ttk.LabelFrame(self.wifi_tab, text="Attack Settings")
        attack_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(attack_frame, text="Max Password Length:").grid(row=0, column=0, padx=5, sticky='e')
        self.max_len = ttk.Combobox(attack_frame, values=list(range(1, 13)), width=5)
        self.max_len.current(7)  # Default to 8
        self.max_len.grid(row=0, column=1, padx=5, sticky='w')

        self.attack_btn = ttk.Button(attack_frame, text="Start WiFi Attack", command=self.start_wifi_attack_thread)
        self.attack_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = ttk.Button(attack_frame, text="Stop Attack", command=self.stop_attack_func, state='disabled')
        self.stop_btn.grid(row=0, column=3, padx=5)

        # WiFi Results Frame
        wifi_results_frame = ttk.LabelFrame(self.wifi_tab, text="Attack Progress")
        wifi_results_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.wifi_results_text = tk.Text(wifi_results_frame, height=10, wrap='word')
        self.wifi_results_text.pack(fill='both', expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(wifi_results_frame, command=self.wifi_results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.wifi_results_text.config(yscrollcommand=scrollbar.set)

    def start_scan_thread(self):
        if not self.scanning:
            threading.Thread(target=self.scan_wifi_networks, daemon=True).start()

    def start_wifi_attack_thread(self):
        if not self.attacking:
            threading.Thread(target=self.start_wifi_attack, daemon=True).start()

    def stop_attack_func(self):
        self.stop_attack = True
        self.wifi_results_text.insert(tk.END, "\nAttack stopped by user\n")

    def scan_wifi_networks(self):
        if self.scanning:
            return

        self.scanning = True
        self.wifi_tree.delete(*self.wifi_tree.get_children())
        self.wifi_results_text.delete(1.0, tk.END)
        self.wifi_results_text.insert(tk.END, "Scanning for WiFi networks...\n")
        self.root.update()

        try:
            # This command works on Windows
            result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                                    capture_output=True, text=True, encoding='utf-8')

            if result.returncode != 0:
                self.wifi_results_text.insert(tk.END,
                                              "Error scanning WiFi networks. Try running as administrator.\n")
                return

            # Parse the output
            networks = []
            current_network = {}

            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('SSID'):
                    if current_network:
                        networks.append(current_network)
                    current_network = {'SSID': line.split(':')[1].strip()}
                elif line.startswith('Signal'):
                    current_network['Signal'] = line.split(':')[1].strip()
                elif line.startswith('Authentication'):
                    current_network['Security'] = line.split(':')[1].strip()
                elif line.startswith('BSSID'):
                    if 'BSSID' not in current_network:
                        current_network['BSSID'] = line.split(':')[1].strip()

            if current_network:
                networks.append(current_network)

            if not networks:
                self.wifi_results_text.insert(tk.END, "No WiFi networks found or access denied.\n")
                return

            # Add to treeview
            for network in networks:
                ssid = network.get('SSID', 'Hidden Network')
                signal = network.get('Signal', 'N/A')
                security = network.get('Security', 'N/A')
                self.wifi_tree.insert('', 'end', values=(ssid, signal, security))

            self.wifi_results_text.insert(tk.END, f"Found {len(networks)} networks.\n")

        except Exception as e:
            self.wifi_results_text.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            self.scanning = False

    def brute_force_password_cracker(self, target_password, max_length=8):
        characters = string.ascii_letters + string.digits + string.punctuation
        attempts = 0
        start_time = time.time()

        for password_length in range(1, max_length + 1):
            if self.stop_attack:
                return None, attempts, None

            for guess in itertools.product(characters, repeat=password_length):
                if self.stop_attack:
                    return None, attempts, None

                attempts += 1
                guess = ''.join(guess)

                # Update GUI every 100 attempts
                if attempts % 100 == 0:
                    self.wifi_results_text.insert(tk.END,
                                                  f"Trying length {password_length}, Attempts: {attempts}, Current: {guess}\n")
                    self.wifi_results_text.see(tk.END)
                    self.root.update()

                if guess == target_password:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    return guess, attempts, time_taken

        return None, attempts, None

    def start_brute_force(self):
        target_password = self.password_entry.get()
        if not target_password:
            messagebox.showerror("Error", "Please enter a target password")
            return

        max_length = int(self.max_len_bf.get())

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Starting brute force attack on: {target_password}\n")
        self.root.update()

        hacked_password, attempts, time_taken = self.brute_force_password_cracker(target_password, max_length)

        if hacked_password:
            self.results_text.insert(tk.END,
                                     f"\nPassword '{hacked_password}' was hacked in {attempts} attempts and {time_taken:.2f} seconds.")
        else:
            self.results_text.insert(tk.END, "\nFailed to hack the password with current settings.")

    def start_wifi_attack(self):
        selected = self.wifi_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a WiFi network first")
            return

        item = self.wifi_tree.item(selected[0])
        target_ssid = item['values'][0]
        max_length = int(self.max_len.get())

        # Check if it's an open network
        if item['values'][2] == 'Open':
            messagebox.showinfo("Info", f"Network {target_ssid} is open (no password needed)")
            return

        self.attacking = True
        self.stop_attack = False
        self.attack_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        self.wifi_results_text.delete(1.0, tk.END)
        self.wifi_results_text.insert(tk.END,
                                      f"Starting attack on {target_ssid} with max password length {max_length}\n")
        self.wifi_results_text.insert(tk.END,
                                      "NOTE: This is a simulation. Actual WiFi cracking requires different techniques.\n")
        self.root.update()

        # Simulate WiFi attack (in reality, you'd need to use tools like aircrack-ng)
        hacked_password, attempts, time_taken = self.brute_force_password_cracker("dummypass", max_length)

        self.attacking = False
        self.attack_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

        if hacked_password:
            self.wifi_results_text.insert(tk.END,
                                          f"\nSimulation complete. Found password '{hacked_password}' in {attempts} attempts.\n")
        else:
            if self.stop_attack:
                self.wifi_results_text.insert(tk.END, "\nAttack stopped by user.\n")
            else:
                self.wifi_results_text.insert(tk.END,
                                              "\nSimulation complete. Password not found with current settings.\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCrackerApp(root)
    root.mainloop()
