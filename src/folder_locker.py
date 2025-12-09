import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import hashlib
import subprocess
import random
import string
import shutil
from datetime import datetime
from pathlib import Path
import threading

class FolderLockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Secure Folder Locker - Kelompok 1 - IF-D")
        self.root.geometry("850x700")
        self.root.resizable(True, True)
        self.root.minsize(800, 650)
        
        # Set icon
        try:
            self.root.iconbitmap(default='assets/icon.ico')
        except:
            pass
        
        # Load data
        self.data_file = "secure_folders_data.json"
        self.locked_folders = self.load_data()
        
        # Security salt
        self.salt = "Kelompok13_SistemOperasi_2025"
        
        # Setup modern style
        self.setup_styles()
        
        # Build UI
        self.setup_ui()
        
        # Center window
        self.center_window()
        
        # Start auto-save
        self.auto_save()
    
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        
        # Try to use modern theme
        try:
            style.theme_use('vista')
        except:
            try:
                style.theme_use('clam')
            except:
                pass
        
        # Custom colors
        self.bg_color = "#f8f9fa"
        self.primary_color = "#4361ee"
        self.secondary_color = "#3a0ca3"
        self.success_color = "#4cc9f0"
        self.danger_color = "#f72585"
        self.warning_color = "#f8961e"
        self.dark_color = "#212529"
        self.light_color = "#e9ecef"
        
        # Configure styles
        style.configure("Primary.TFrame", background=self.primary_color)
        style.configure("Secondary.TFrame", background=self.secondary_color)
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="white")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#dee2e6")
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.dark_color)
        style.configure("Info.TLabel", font=("Segoe UI", 9), foreground="#6c757d")
        
        # Button styles
        style.configure("Primary.TButton", 
                       font=("Segoe UI", 10, "bold"),
                       padding=10,
                       background=self.primary_color,
                       foreground="white")
        style.map("Primary.TButton",
                 background=[('active', self.secondary_color)])
        
        style.configure("Success.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=10,
                       background="#28a745",
                       foreground="white")
        
        style.configure("Danger.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=10,
                       background=self.danger_color,
                       foreground="white")
        
        self.root.configure(bg=self.bg_color)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup modern user interface"""
        # Create main container with scrollbar
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ========== HEADER SECTION ==========
        header_frame = tk.Frame(scrollable_frame, bg=self.primary_color, 
                               height=120, relief="flat")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🔐 SECURE FOLDER LOCKER",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg=self.primary_color,
            pady=20
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Sistem Operasi - Kelompok 1 - IF-D | Proteksi Folder dengan Enkripsi Tingkat Tinggi",
            font=("Segoe UI", 10),
            fg="#dee2e6",
            bg=self.primary_color
        )
        subtitle_label.pack()
        
        # Stats bar
        stats_frame = tk.Frame(header_frame, bg=self.secondary_color, height=40)
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X)
        stats_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="📊 Folder Terkunci: 0 | Status: Ready",
            font=("Segoe UI", 9),
            fg="white",
            bg=self.secondary_color,
            padx=20
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # ========== MAIN CONTENT ==========
        content_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Controls
        left_panel = tk.Frame(content_frame, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Folder Selection Card
        folder_card = tk.Frame(left_panel, bg="white", relief="solid", 
                              borderwidth=1, padx=20, pady=20)
        folder_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            folder_card,
            text="📁 PILIH FOLDER",
            font=("Segoe UI", 11, "bold"),
            fg=self.dark_color,
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Path display
        path_frame = tk.Frame(folder_card, bg="white")
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_path = tk.StringVar()
        
        # Custom entry with icon
        entry_frame = tk.Frame(path_frame, bg="#e9ecef", relief="sunken", 
                              borderwidth=1, padx=10, pady=8)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        path_label = tk.Label(
            entry_frame,
            textvariable=self.folder_path,
            font=("Consolas", 9),
            bg="#e9ecef",
            fg="#495057",
            anchor=tk.W,
            relief="flat"
        )
        path_label.pack(fill=tk.X)
        
        # Browse button with icon
        browse_btn = tk.Button(
            path_frame,
            text="📂 Browse",
            font=("Segoe UI", 9, "bold"),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.browse_folder
        )
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Password Card
        password_card = tk.Frame(left_panel, bg="white", relief="solid", 
                                borderwidth=1, padx=20, pady=20)
        password_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            password_card,
            text="🔑 PASSWORD",
            font=("Segoe UI", 11, "bold"),
            fg=self.dark_color,
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Password input with strength indicator
        tk.Label(
            password_card,
            text="Password:",
            font=("Segoe UI", 10),
            fg="#495057",
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_var.trace('w', self.update_password_strength)
        
        pass_frame = tk.Frame(password_card, bg="white")
        pass_frame.pack(fill=tk.X, pady=(0, 10))
        
        pass_entry = tk.Entry(
            pass_frame,
            textvariable=self.password_var,
            show="•",
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Show password button
        self.show_pass_btn = tk.Button(
            pass_frame,
            text="👁",
            font=("Segoe UI", 9),
            width=3,
            relief="flat",
            bg="#e9ecef",
            command=lambda: self.toggle_password(pass_entry, None)
        )
        self.show_pass_btn.pack(side=tk.RIGHT)
        
        # Password strength indicator
        self.strength_frame = tk.Frame(password_card, bg="white", height=5)
        self.strength_frame.pack(fill=tk.X, pady=(0, 15))
        self.strength_frame.pack_propagate(False)
        
        self.strength_bar = tk.Frame(self.strength_frame, bg="#dc3545", width=0)
        self.strength_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        self.strength_label = tk.Label(
            password_card,
            text="Password strength: Weak",
            font=("Segoe UI", 8),
            fg="#dc3545",
            bg="white"
        )
        self.strength_label.pack(anchor=tk.W)
        
        # Confirm Password
        tk.Label(
            password_card,
            text="Konfirmasi Password:",
            font=("Segoe UI", 10),
            fg="#495057",
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.confirm_pass_var = tk.StringVar()
        
        confirm_frame = tk.Frame(password_card, bg="white")
        confirm_frame.pack(fill=tk.X)
        
        confirm_entry = tk.Entry(
            confirm_frame,
            textvariable=self.confirm_pass_var,
            show="•",
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Show confirm password button
        self.show_confirm_btn = tk.Button(
            confirm_frame,
            text="👁",
            font=("Segoe UI", 9),
            width=3,
            relief="flat",
            bg="#e9ecef",
            command=lambda: self.toggle_password(None, confirm_entry)
        )
        self.show_confirm_btn.pack(side=tk.RIGHT)
        
        # Action Buttons Card
        action_card = tk.Frame(left_panel, bg="white", relief="solid", 
                              borderwidth=1, padx=20, pady=20)
        action_card.pack(fill=tk.X)
        
        button_frame = tk.Frame(action_card, bg="white")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Lock button with icon
        self.lock_btn = tk.Button(
            button_frame,
            text="🔒 KUNCI FOLDER",
            font=("Segoe UI", 11, "bold"),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.lock_folder
        )
        self.lock_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Unlock button with icon
        self.unlock_btn = tk.Button(
            button_frame,
            text="🔓 BUKA KUNCI",
            font=("Segoe UI", 11, "bold"),
            bg=self.success_color,
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.unlock_folder
        )
        self.unlock_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Status Card
        status_card = tk.Frame(left_panel, bg="white", relief="solid", 
                              borderwidth=1, padx=20, pady=20)
        status_card.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            status_card,
            text="📊 STATUS SISTEM",
            font=("Segoe UI", 11, "bold"),
            fg=self.dark_color,
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_card,
            text="✅ Sistem siap. Pilih folder untuk memulai.",
            font=("Segoe UI", 10),
            fg="#28a745",
            bg="white",
            wraplength=300,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W)
        
        # ========== RIGHT PANEL - LOCKED FOLDERS ==========
        right_panel = tk.Frame(content_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        list_card = tk.Frame(right_panel, bg="white", relief="solid", 
                            borderwidth=1, padx=20, pady=20)
        list_card.pack(fill=tk.BOTH, expand=True)
        
        # Header with refresh button
        header_frame = tk.Frame(list_card, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header_frame,
            text="📋 FOLDER TERKUNCI",
            font=("Segoe UI", 11, "bold"),
            fg=self.dark_color,
            bg="white"
        ).pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=("Segoe UI", 9),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.refresh_list
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Treeview with modern styling
        tree_frame = tk.Frame(list_card, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define columns
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('No', 'Nama', 'Lokasi', 'Tanggal', 'Status'),
            show='headings',
            height=15
        )
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 9, "bold"),
                       background=self.light_color,
                       foreground=self.dark_color)
        style.configure("Treeview",
                       font=("Segoe UI", 9),
                       rowheight=25)
        
        # Define headings
        self.tree.heading('No', text='No', anchor=tk.CENTER)
        self.tree.heading('Nama', text='Nama Folder', anchor=tk.W)
        self.tree.heading('Lokasi', text='Lokasi', anchor=tk.W)
        self.tree.heading('Tanggal', text='Tanggal', anchor=tk.CENTER)
        self.tree.heading('Status', text='Status', anchor=tk.CENTER)
        
        # Define columns
        self.tree.column('No', width=50, anchor=tk.CENTER)
        self.tree.column('Nama', width=150, anchor=tk.W)
        self.tree.column('Lokasi', width=200, anchor=tk.W)
        self.tree.column('Tanggal', width=120, anchor=tk.CENTER)
        self.tree.column('Status', width=80, anchor=tk.CENTER)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(scrollable_frame, bg=self.dark_color, height=50)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        footer_frame.pack_propagate(False)
        
        tk.Label(
            footer_frame,
            text="©INFORMATIKA 2025 Kelompok 1 - IF-D - Sistem Operasi | Aplikasi Pengunci Folder dengan Keamanan Tinggi",
            font=("Segoe UI", 8),
            fg="#adb5bd",
            bg=self.dark_color
        ).pack(expand=True)
        
        # Load initial data
        self.refresh_list()
        self.update_stats()
    
    def update_password_strength(self, *args):
        """Update password strength indicator"""
        password = self.password_var.get()
        if not password:
            self.strength_bar.config(bg="#e9ecef", width=0)
            self.strength_label.config(text="Password strength: None", fg="#6c757d")
            return
        
        # Calculate strength
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        strength = 0
        if length >= 8:
            strength += 1
        if length >= 12:
            strength += 1
        if has_upper and has_lower:
            strength += 1
        if has_digit:
            strength += 1
        if has_special:
            strength += 1
        
        # Update UI
        width = strength * 60  # 60px per strength level
        colors = {
            0: "#dc3545",  # Weak (red)
            1: "#dc3545",
            2: "#fd7e14",  # Medium (orange)
            3: "#ffc107",  # Fair (yellow)
            4: "#28a745",  # Strong (green)
            5: "#20c997"   # Very strong (teal)
        }
        labels = {
            0: "Very Weak",
            1: "Weak",
            2: "Medium",
            3: "Fair",
            4: "Strong",
            5: "Very Strong"
        }
        
        color = colors.get(strength, "#dc3545")
        label = labels.get(strength, "Weak")
        
        self.strength_bar.config(bg=color, width=width)
        self.strength_label.config(text=f"Password strength: {label}", fg=color)
    
    def toggle_password(self, pass_entry=None, confirm_entry=None):
        """Toggle password visibility"""
        if pass_entry:
            current_show = pass_entry.cget('show')
            pass_entry.config(show='' if current_show == '•' else '•')
            self.show_pass_btn.config(text="👁‍🗨" if current_show == '•' else "👁")
        
        if confirm_entry:
            current_show = confirm_entry.cget('show')
            confirm_entry.config(show='' if current_show == '•' else '•')
            self.show_confirm_btn.config(text="👁‍🗨" if current_show == '•' else "👁")
    
    def browse_folder(self):
        """Open folder dialog"""
        folder = filedialog.askdirectory(
            title="Pilih folder yang akan dikunci",
            mustexist=True
        )
        if folder:
            self.folder_path.set(folder)
            self.status_label.config(
                text=f"✅ Folder dipilih: {os.path.basename(folder)}",
                fg="#28a745"
            )
    
    # ========== SECURITY FUNCTIONS ==========
    
    def hash_password(self, password):
        """Hash password with salt using SHA-256"""
        return hashlib.sha256((password + self.salt).encode()).hexdigest()
    
    def generate_random_name(self, original_name):
        """Generate random hidden name"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        name_hash = hashlib.md5(original_name.encode()).hexdigest()[:8]
        return f".{random_str}_{name_hash}"
    
    def load_data(self):
        """Load locked folders data from JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
        return {}
    
    def save_data(self):
        """Save locked folders data to JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.locked_folders, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def auto_save(self):
        """Auto-save data every 30 seconds"""
        if self.save_data():
            pass  # Success
        self.root.after(30000, self.auto_save)  # Save every 30 seconds
    
    def update_stats(self):
        """Update statistics display"""
        locked_count = len(self.locked_folders)
        self.stats_label.config(
            text=f"📊 Folder Terkunci: {locked_count} | Status: {'Aktif' if locked_count > 0 else 'Siap'}"
        )
    
    # ========== LOCK/UNLOCK FUNCTIONS ==========
    
    def lock_folder(self):
        """Lock folder securely with rename + hidden + system attributes"""
        folder_path = self.folder_path.get()
        password = self.password_var.get()
        confirm = self.confirm_pass_var.get()
        
        # Validation
        if not folder_path:
            messagebox.showwarning("Peringatan", "Pilih folder terlebih dahulu!")
            return
        
        if not password:
            messagebox.showwarning("Peringatan", "Password tidak boleh kosong!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Password tidak cocok!")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Peringatan", "Password minimal 4 karakter!")
            return
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Folder tidak ditemukan!")
            return
        
        # Check if already locked
        folder_name = os.path.basename(folder_path)
        for data in self.locked_folders.values():
            if data['original_path'] == folder_path:
                messagebox.showwarning("Peringatan", "Folder sudah terkunci!")
                return
        
        try:
            # Generate secure data
            parent_dir = os.path.dirname(folder_path)
            hidden_name = self.generate_random_name(folder_name)
            hidden_path = os.path.join(parent_dir, hidden_name)
            
            # 1. Rename folder to random hidden name
            os.rename(folder_path, hidden_path)
            
            # 2. Set hidden + system attributes (more secure)
            subprocess.run(
                f'attrib +h +s "{hidden_path}"',
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 3. Create decoy folder with original name
            decoy_path = folder_path
            os.makedirs(decoy_path, exist_ok=True)
            
            # Create warning file in decoy folder
            warning_file = os.path.join(decoy_path, "!!!PERINGATAN!!!.txt")
            with open(warning_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("⚠️   PERINGATAN KEAMANAN   ⚠️\n")
                f.write("=" * 60 + "\n\n")
                f.write("Folder ini telah DIKUNCI oleh sistem keamanan.\n")
                f.write("Konten asli telah diamankan dan disembunyikan.\n\n")
                f.write("Untuk mengakses folder asli:\n")
                f.write("1. Jalankan aplikasi 'Secure Folder Locker'\n")
                f.write("2. Masukkan password yang benar\n")
                f.write("3. Pilih folder dari daftar dan klik 'Buka Kunci'\n\n")
                f.write("=" * 60 + "\n")
                f.write(f"ID: {hashlib.md5(folder_path.encode()).hexdigest()[:12]}\n")
                f.write(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n")
            
            # Hide decoy folder and warning file
            subprocess.run(
                f'attrib +h "{decoy_path}"',
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            subprocess.run(
                f'attrib +h "{warning_file}"',
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Save to database
            lock_id = hashlib.md5(folder_path.encode()).hexdigest()
            self.locked_folders[lock_id] = {
                'original_name': folder_name,
                'original_path': folder_path,
                'hidden_name': hidden_name,
                'hidden_path': hidden_path,
                'parent_dir': parent_dir,
                'password_hash': self.hash_password(password),
                'locked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'lock_method': 'secure_rename'
            }
            
            self.save_data()
            
            # Update UI
            self.status_label.config(
                text=f"✅ Folder '{folder_name}' berhasil dikunci dengan aman!",
                fg="#28a745"
            )
            messagebox.showinfo(
                "Sukses",
                f"✅ Folder '{folder_name}' berhasil dikunci!\n\n"
                f"• Folder asli telah disembunyikan\n"
                f"• Nama folder diubah secara acak\n"
                f"• Atribut sistem diterapkan\n"
                f"• Tidak dapat diakses via direct path\n\n"
                f"⚠️ Catat password Anda dengan baik!"
            )
            
            # Clear fields and refresh
            self.folder_path.set("")
            self.password_var.set("")
            self.confirm_pass_var.set("")
            self.refresh_list()
            self.update_stats()
            self.update_password_strength()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"❌ Gagal mengunci folder:\n\n{str(e)}\n\n"
                f"Coba jalankan aplikasi sebagai Administrator."
            )
    
    def unlock_folder(self):
        """Unlock selected folder"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih folder dari daftar terlebih dahulu!")
            return
        
        item = self.tree.item(selection[0])
        folder_name = item['values'][1]
        
        # Ask for password
        from tkinter import simpledialog
        password = simpledialog.askstring(
            "Password Required",
            f"Masukkan password untuk membuka folder:\n\n{folder_name}",
            show='*'
        )
        
        if not password:
            return
        
        # Find matching folder
        lock_id = None
        folder_data = None
        
        for lid, data in self.locked_folders.items():
            if data['original_name'] == folder_name:
                if self.hash_password(password) == data['password_hash']:
                    lock_id = lid
                    folder_data = data
                    break
        
        if not lock_id or not folder_data:
            messagebox.showerror("Error", "Password salah atau folder tidak ditemukan!")
            return
        
        try:
            hidden_path = folder_data['hidden_path']
            original_path = folder_data['original_path']
            decoy_path = original_path
            
            # 1. Remove attributes from hidden folder
            subprocess.run(
                f'attrib -h -s "{hidden_path}"',
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 2. Delete decoy folder if exists
            if os.path.exists(decoy_path):
                try:
                    # Remove hidden attribute first
                    subprocess.run(
                        f'attrib -h "{decoy_path}"',
                        shell=True,
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    # Delete decoy folder
                    shutil.rmtree(decoy_path)
                except:
                    pass
            
            # 3. Rename back to original
            if os.path.exists(hidden_path):
                os.rename(hidden_path, original_path)
            
            # 4. Remove from database
            del self.locked_folders[lock_id]
            self.save_data()
            
            # Update UI
            self.status_label.config(
                text=f"✅ Folder '{folder_name}' berhasil dibuka!",
                fg="#28a745"
            )
            messagebox.showinfo(
                "Sukses",
                f"✅ Folder '{folder_name}' berhasil dibuka kuncinya!\n\n"
                f"Folder sekarang dapat diakses di lokasi aslinya."
            )
            
            # Refresh
            self.refresh_list()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"❌ Gagal membuka folder:\n\n{str(e)}\n\n"
                f"Coba jalankan aplikasi sebagai Administrator."
            )
    
    def on_tree_double_click(self, event):
        """Handle double click on tree item"""
        selection = self.tree.selection()
        if selection:
            self.unlock_folder()
    
    def refresh_list(self):
        """Refresh locked folders list"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items
        for i, (lock_id, data) in enumerate(self.locked_folders.items(), 1):
            folder_name = data['original_name']
            folder_path = data['original_path']
            date = data['locked_date']
            
            # Check if folder is still properly hidden
            hidden_path = data['hidden_path']
            status = "✅ Aman"
            status_color = "#28a745"
            
            try:
                # Check if hidden folder still exists
                if not os.path.exists(hidden_path):
                    status = "⚠️ Risiko"
                    status_color = self.warning_color
                else:
                    # Check attributes
                    result = subprocess.run(
                        f'attrib "{hidden_path}"',
                        shell=True,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if "H" not in result.stdout or "S" not in result.stdout:
                        status = "⚠️ Terbuka"
                        status_color = self.warning_color
            except:
                status = "❓ Unknown"
                status_color = "#6c757d"
            
            # Insert into tree
            item_id = self.tree.insert('', 'end', values=(
                i,
                folder_name,
                os.path.dirname(folder_path),
                date,
                status
            ))
            
            # Color code based on status
            if status == "✅ Aman":
                self.tree.item(item_id, tags=('safe',))
            elif status == "⚠️ Risiko":
                self.tree.item(item_id, tags=('warning',))
            elif status == "⚠️ Terbuka":
                self.tree.item(item_id, tags=('danger',))
            else:
                self.tree.item(item_id, tags=('unknown',))
        
        # Configure tags for colors
        self.tree.tag_configure('safe', background='#d4edda')
        self.tree.tag_configure('warning', background='#fff3cd')
        self.tree.tag_configure('danger', background='#f8d7da')
        self.tree.tag_configure('unknown', background='#e9ecef')

def main():
    """Main function"""
    # Create and run the application
    root = tk.Tk()
    
    # Set Windows taskbar icon
    try:
        import ctypes
        myappid = 'Kelompok13.FolderLocker.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    
    app = FolderLockerApp(root)
    
    # Handle window close
    def on_closing():
        if messagebox.askyesno("Keluar", "Apakah Anda yakin ingin keluar?\n\nData akan otomatis disimpan."):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()