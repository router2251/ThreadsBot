#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import time
from datetime import datetime
import queue
from android_engagement import AndroidEngagement
import uiautomator2 as u2
import os
import sys
import logging
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_gui.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class LoginManager:
    def __init__(self, parent):
        self.parent = parent
        self.accounts = []
        self.load_accounts()
        
    def load_accounts(self):
        try:
            if os.path.exists("accounts_config.json"):
                with open("accounts_config.json", "r") as f:
                    self.accounts = json.load(f)
        except Exception as e:
            self.accounts = []
            
    def save_accounts(self):
        with open("accounts_config.json", "w") as f:
            json.dump(self.accounts, f, indent=4)

class BotGUI:
    def __init__(self, root):
        print("[DEBUG] BotGUI.__init__ started")
        self.root = root
        self.root.title("Threads Bot Manager")
        self.root.geometry("1200x800")
        print("[DEBUG] Window title and geometry set")
        
        # Set a light theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme for better visibility
        
        # Configure colors
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', foreground='black')
        self.style.configure('TButton', background='#4a90e2', foreground='white')
        
        # Initialize managers
        self.login_manager = LoginManager(self)
        print("[DEBUG] LoginManager initialized")
        self.bot = AndroidEngagement()
        print("[DEBUG] AndroidEngagement initialized")
        self.action_queue = queue.Queue()
        self.is_running = False
        
        # Create main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        print("[DEBUG] Main container created and packed")
        
        # Left panel for device list and controls
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=1)
        
        # Right panel for logs and stats
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel, weight=2)
        print("[DEBUG] Panels created and added")
        
        self.setup_left_panel()
        print("[DEBUG] Left panel set up")
        self.setup_right_panel()
        print("[DEBUG] Right panel set up")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        print("[DEBUG] Update thread started")

    def setup_left_panel(self):
        # Test Label
        test_label = ttk.Label(self.left_panel, text="Test Label - Left Panel", font=('Arial', 14))
        test_label.pack(pady=10)
        
        # Login Management
        login_frame = ttk.LabelFrame(self.left_panel, text="Account Management")
        login_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Account List
        self.account_list = ttk.Treeview(login_frame, columns=("Username", "Status"), show="headings", height=3)
        self.account_list.heading("Username", text="Username")
        self.account_list.heading("Status", text="Status")
        self.account_list.pack(fill=tk.X, padx=5, pady=5)
        
        # Account Controls
        account_controls = ttk.Frame(login_frame)
        account_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(account_controls, text="Add Account", command=self.show_add_account_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_controls, text="Edit Account", command=self.show_edit_account_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_controls, text="Remove Account", command=self.remove_account).pack(side=tk.LEFT, padx=2)
        
        # Device List
        device_frame = ttk.LabelFrame(self.left_panel, text="Connected Devices")
        device_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.device_list = ttk.Treeview(device_frame, columns=("Status", "Actions"), show="headings")
        self.device_list.heading("Status", text="Status")
        self.device_list.heading("Actions", text="Actions")
        self.device_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control Buttons
        control_frame = ttk.Frame(self.left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(control_frame, text="Refresh Devices", command=self.refresh_devices)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Configuration
        config_frame = ttk.LabelFrame(self.left_panel, text="Configuration")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Viral thresholds
        ttk.Label(config_frame, text="Min Likes:").grid(row=0, column=0, padx=5, pady=2)
        self.min_likes_var = tk.StringVar(value=str(self.bot.min_likes_for_viral))
        ttk.Entry(config_frame, textvariable=self.min_likes_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Min Comments:").grid(row=1, column=0, padx=5, pady=2)
        self.min_comments_var = tk.StringVar(value=str(self.bot.min_comments_for_viral))
        ttk.Entry(config_frame, textvariable=self.min_comments_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Cooldowns
        ttk.Label(config_frame, text="Comment Cooldown (s):").grid(row=2, column=0, padx=5, pady=2)
        self.comment_cooldown_var = tk.StringVar(value=str(self.bot.comment_cooldown))
        ttk.Entry(config_frame, textvariable=self.comment_cooldown_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Follow Cooldown (s):").grid(row=3, column=0, padx=5, pady=2)
        self.follow_cooldown_var = tk.StringVar(value=str(self.bot.follow_cooldown))
        ttk.Entry(config_frame, textvariable=self.follow_cooldown_var, width=10).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Like Cooldown (s):").grid(row=4, column=0, padx=5, pady=2)
        self.like_cooldown_var = tk.StringVar(value=str(self.bot.like_cooldown))
        ttk.Entry(config_frame, textvariable=self.like_cooldown_var, width=10).grid(row=4, column=1, padx=5, pady=2)
        
        # Save config button
        ttk.Button(config_frame, text="Save Config", command=self.save_config).grid(row=5, column=0, columnspan=2, pady=5)
        
        # Refresh account list
        self.refresh_account_list()

    def show_add_account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Account")
        dialog.geometry("400x500")
        
        # Account details
        ttk.Label(dialog, text="Username:").pack(padx=5, pady=2)
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(dialog, text="Password:").pack(padx=5, pady=2)
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="*").pack(fill=tk.X, padx=5, pady=2)
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(dialog, text="Proxy Settings")
        proxy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(proxy_frame, text="Host:").pack(padx=5, pady=2)
        proxy_host_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=proxy_host_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Port:").pack(padx=5, pady=2)
        proxy_port_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=proxy_port_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Username:").pack(padx=5, pady=2)
        proxy_user_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=proxy_user_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Password:").pack(padx=5, pady=2)
        proxy_pass_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=proxy_pass_var, show="*").pack(fill=tk.X, padx=5, pady=2)
        
        # Device settings
        device_frame = ttk.LabelFrame(dialog, text="Device Settings")
        device_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(device_frame, text="Device Name:").pack(padx=5, pady=2)
        device_name_var = tk.StringVar()
        ttk.Entry(device_frame, textvariable=device_name_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(device_frame, text="Serial Number:").pack(padx=5, pady=2)
        device_serial_var = tk.StringVar()
        ttk.Entry(device_frame, textvariable=device_serial_var).pack(fill=tk.X, padx=5, pady=2)
        
        def save_account():
            account = {
                "username": username_var.get(),
                "password": password_var.get(),
                "proxy": {
                    "host": proxy_host_var.get(),
                    "port": proxy_port_var.get(),
                    "username": proxy_user_var.get(),
                    "password": proxy_pass_var.get()
                },
                "device": {
                    "name": device_name_var.get(),
                    "serial": device_serial_var.get()
                }
            }
            
            self.login_manager.accounts.append(account)
            self.login_manager.save_accounts()
            self.refresh_account_list()
            dialog.destroy()
            self.log(f"Added account: {account['username']}")
        
        ttk.Button(dialog, text="Save", command=save_account).pack(pady=10)

    def show_edit_account_dialog(self):
        selection = self.account_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to edit")
            return
            
        account_index = self.account_list.index(selection[0])
        account = self.login_manager.accounts[account_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Account")
        dialog.geometry("400x500")
        
        # Account details
        ttk.Label(dialog, text="Username:").pack(padx=5, pady=2)
        username_var = tk.StringVar(value=account["username"])
        ttk.Entry(dialog, textvariable=username_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(dialog, text="Password:").pack(padx=5, pady=2)
        password_var = tk.StringVar(value=account["password"])
        ttk.Entry(dialog, textvariable=password_var, show="*").pack(fill=tk.X, padx=5, pady=2)
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(dialog, text="Proxy Settings")
        proxy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(proxy_frame, text="Host:").pack(padx=5, pady=2)
        proxy_host_var = tk.StringVar(value=account["proxy"]["host"])
        ttk.Entry(proxy_frame, textvariable=proxy_host_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Port:").pack(padx=5, pady=2)
        proxy_port_var = tk.StringVar(value=account["proxy"]["port"])
        ttk.Entry(proxy_frame, textvariable=proxy_port_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Username:").pack(padx=5, pady=2)
        proxy_user_var = tk.StringVar(value=account["proxy"]["username"])
        ttk.Entry(proxy_frame, textvariable=proxy_user_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(proxy_frame, text="Password:").pack(padx=5, pady=2)
        proxy_pass_var = tk.StringVar(value=account["proxy"]["password"])
        ttk.Entry(proxy_frame, textvariable=proxy_pass_var, show="*").pack(fill=tk.X, padx=5, pady=2)
        
        # Device settings
        device_frame = ttk.LabelFrame(dialog, text="Device Settings")
        device_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(device_frame, text="Device Name:").pack(padx=5, pady=2)
        device_name_var = tk.StringVar(value=account["device"]["name"])
        ttk.Entry(device_frame, textvariable=device_name_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(device_frame, text="Serial Number:").pack(padx=5, pady=2)
        device_serial_var = tk.StringVar(value=account["device"]["serial"])
        ttk.Entry(device_frame, textvariable=device_serial_var).pack(fill=tk.X, padx=5, pady=2)
        
        def save_changes():
            account["username"] = username_var.get()
            account["password"] = password_var.get()
            account["proxy"] = {
                "host": proxy_host_var.get(),
                "port": proxy_port_var.get(),
                "username": proxy_user_var.get(),
                "password": proxy_pass_var.get()
            }
            account["device"] = {
                "name": device_name_var.get(),
                "serial": device_serial_var.get()
            }
            
            self.login_manager.save_accounts()
            self.refresh_account_list()
            dialog.destroy()
            self.log(f"Updated account: {account['username']}")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)

    def remove_account(self):
        selection = self.account_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to remove")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this account?"):
            account_index = self.account_list.index(selection[0])
            account = self.login_manager.accounts.pop(account_index)
            self.login_manager.save_accounts()
            self.refresh_account_list()
            self.log(f"Removed account: {account['username']}")

    def refresh_account_list(self):
        self.account_list.delete(*self.account_list.get_children())
        for account in self.login_manager.accounts:
            self.account_list.insert("", tk.END, text=account["username"], 
                                   values=(account["username"], "Inactive"))

    def setup_right_panel(self):
        # Test Label
        test_label = ttk.Label(self.right_panel, text="Test Label - Right Panel", font=('Arial', 14))
        test_label.pack(pady=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.right_panel, text="Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=5)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(self.right_panel, text="Activity Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=lambda: self.log_text.delete(1.0, tk.END)).pack(pady=5)

    def refresh_devices(self):
        self.device_list.delete(*self.device_list.get_children())
        for device_name, device in self.bot.active_devices.items():
            status = "Connected" if device.info else "Disconnected"
            self.device_list.insert("", tk.END, text=device_name, values=(status, "0"))

    def start_bot(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Start bot in separate thread
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()
            
            self.log("Bot started")

    def stop_bot(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("Bot stopped")

    def run_bot(self):
        while self.is_running:
            try:
                # Connect to devices and run engagement
                for device_name in self.bot.devices:
                    device = self.bot.connect_device(device_name)
                    if device:
                        # Open Threads app
                        self.bot.open_threads_app(device)
                        
                        # Scan feed for viral posts
                        viral_posts = self.bot.scan_feed(device)
                        self.log(f"Found {len(viral_posts)} viral posts on {device_name}")
                        
                        # Process each viral post
                        for post in viral_posts:
                            if self.is_running:  # Check if bot is still running
                                self.bot.process_post(device, device_name, post)
                                time.sleep(2)  # Add delay between posts
                
                time.sleep(10)  # Wait before next scan cycle
            except Exception as e:
                self.log(f"Error in bot loop: {str(e)}")
                time.sleep(5)

    def save_config(self):
        try:
            self.bot.min_likes_for_viral = int(self.min_likes_var.get())
            self.bot.min_comments_for_viral = int(self.min_comments_var.get())
            self.bot.comment_cooldown = int(self.comment_cooldown_var.get())
            self.bot.follow_cooldown = int(self.follow_cooldown_var.get())
            self.bot.like_cooldown = int(self.like_cooldown_var.get())
            
            # Save to config file
            config = {
                "min_likes_for_viral": self.bot.min_likes_for_viral,
                "min_comments_for_viral": self.bot.min_comments_for_viral,
                "comment_cooldown": self.bot.comment_cooldown,
                "follow_cooldown": self.bot.follow_cooldown,
                "like_cooldown": self.bot.like_cooldown
            }
            
            with open("bot_config.json", "w") as f:
                json.dump(config, f, indent=4)
            
            self.log("Configuration saved")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def update_loop(self):
        while True:
            try:
                # Update device status
                for device_name, device in self.bot.active_devices.items():
                    status = "Connected" if device.info else "Disconnected"
                    for item in self.device_list.get_children():
                        if self.device_list.item(item)["text"] == device_name:
                            self.device_list.item(item, values=(status, "0"))
                            break
                
                # Update stats
                stats = f"Active Devices: {len(self.bot.active_devices)}\n"
                stats += f"Last Action: {datetime.now().strftime('%H:%M:%S')}\n"
                stats += f"Total Actions: {sum(1 for _ in self.bot.last_comment_time.values())}\n"
                
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, stats)
                
                time.sleep(1)
            except Exception as e:
                self.log(f"Update error: {str(e)}")
                time.sleep(5)

def main():
    print("[DEBUG] main() started")
    root = tk.Tk()
    print("[DEBUG] tk.Tk() created")
    import tkinter.messagebox
    tkinter.messagebox.showinfo("Startup", "Bot GUI is starting!")
    print("[DEBUG] messagebox shown")
    app = BotGUI(root)
    print("[DEBUG] BotGUI instantiated")
    root.mainloop()
    print("[DEBUG] mainloop exited")

if __name__ == "__main__":
    main() 