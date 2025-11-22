#!/usr/bin/env python3
"""
Enhanced Flashcard App - Now with Images & Resizable Text!
==========================================================

✨ NEW FEATURES::::
- Image attachments on questions AND answers
- Resizable text areas (drag the resize handle)
- Dark/Light theme toggle
- Card tagging system  
- Search across all decks
- Study session history & statistics
- Backup and restore functionality
- All original features preserved!

Requirements:
    pip install Pillow

Run: python flashcard_app_improved.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import random
import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime

# Try to import PIL for image support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("\n⚠️  WARNING: Pillow not installed!")
    print("   Image features will be disabled.")
    print("   Install with: pip install Pillow\n")


class ResizableText(tk.Frame):
    """A text widget with a draggable resize handle at the bottom."""
    
    def __init__(self, parent, height=5, width=70, **kwargs):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')
        
        # Create the text widget
        self.text = tk.Text(self, height=height, width=width, **kwargs)
        self.text.pack(fill='both', expand=True)
        
        # Create the resize handle
        self.resize_handle = tk.Label(
            self, 
            text="⋮⋮⋮ Drag to resize ⋮⋮⋮", 
            cursor="sb_v_double_arrow",
            bg='#ddd',
            fg='#666',
            font=("Arial", 8),
            relief='raised',
            bd=1
        )
        self.resize_handle.pack(fill='x')
        
        # Bind drag events
        self.resize_handle.bind("<Button-1>", self.start_resize)
        self.resize_handle.bind("<B1-Motion>", self.do_resize)
        
        self.start_y = 0
        self.start_height = height
    
    def start_resize(self, event):
        """Start the resize operation."""
        self.start_y = event.y_root
        self.start_height = self.text.winfo_height()
    
    def do_resize(self, event):
        """Perform the resize as user drags."""
        delta = event.y_root - self.start_y
        new_height = max(50, self.start_height + delta)  # Min 50px
        # Convert pixels to lines (roughly)
        self.text.configure(height=max(2, new_height // 20))
    
    def get(self, start, end):
        """Get text content."""
        return self.text.get(start, end)
    
    def insert(self, index, text):
        """Insert text."""
        self.text.insert(index, text)
    
    def delete(self, start, end):
        """Delete text."""
        self.text.delete(start, end)


class FlashcardApp:
    def __init__(self):
        """Initialize the enhanced flashcard application."""
        # Configuration
        self.DATA_FILE = "flashcards_data.json"
        self.IMAGE_DIR = "flashcard_images"
        self.BACKUP_DIR = "flashcard_backups"
        
        # Create directories
        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        
        # Data structure
        self.data = {
            "decks": {},
            "settings": {
                "last_used_deck": None,
                "theme": "light",
                "study_mode": "sequential"
            },
            "tags": [],
            "study_history": []
        }
        
        # Session variables
        self.current_deck = None
        self.current_card_index = 0
        self.study_mode = "sequential"
        self.shuffled_indices = []
        self.show_answer = False
        self.study_cards = []
        self.known_cards = set()
        self.session_start_time = None
        self.current_theme = "light"
        self.image_cache = {}
        
        # Load data
        self.load_data()
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Enhanced Flashcard App - Now with Images!")
        self.root.geometry("1000x750")
        
        self.apply_theme()
        self.create_menu_bar()
        self.create_main_menu()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Deck", command=self.import_deck)
        file_menu.add_command(label="Backup All Data", command=self.backup_data)
        file_menu.add_command(label="Restore from Backup", command=self.restore_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme (Dark/Light)", command=self.toggle_theme)
        view_menu.add_command(label="View All Tags", command=self.view_all_tags)
        view_menu.add_command(label="Study History", command=self.view_study_history)
        
        # Search menu
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Search", menu=search_menu)
        search_menu.add_command(label="Search Cards...", command=self.search_cards)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
    
    def apply_theme(self):
        """Apply the current theme colors."""
        if self.current_theme == "dark":
            self.colors = {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'card_bg': '#3c3c3c',
                'button_bg': '#4a4a4a',
                'accent': '#5c9ead',
                'success': '#6aaf6a',
                'warning': '#e8b84e',
                'danger': '#e85d5d'
            }
        else:  # light theme
            self.colors = {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'card_bg': '#ffffff',
                'button_bg': '#e0e0e0',
                'accent': '#2196F3',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'danger': '#f44336'
            }
        
        self.root.configure(bg=self.colors['bg'])
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.data["settings"]["theme"] = self.current_theme
        self.save_data()
        self.apply_theme()
        self.create_main_menu()
        messagebox.showinfo("Theme Changed", f"Switched to {self.current_theme} mode!")
    
    def load_data(self):
        """Load all flashcard data from JSON."""
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                
                # Merge with defaults
                if "decks" in loaded:
                    self.data["decks"] = loaded["decks"]
                if "settings" in loaded:
                    self.data["settings"].update(loaded["settings"])
                if "tags" in loaded:
                    self.data["tags"] = loaded["tags"]
                if "study_history" in loaded:
                    self.data["study_history"] = loaded["study_history"]
                
                self.current_theme = self.data["settings"].get("theme", "light")
                
                deck_count = len(self.data["decks"])
                total_cards = sum(len(d["cards"]) for d in self.data["decks"].values())
                print(f"✓ Loaded {deck_count} decks with {total_cards} cards")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save all flashcard data to JSON."""
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save: {e}")
    
    def backup_data(self):
        """Create a timestamped backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.BACKUP_DIR, f"backup_{timestamp}.json")
            
            if os.path.exists(self.DATA_FILE):
                shutil.copy(self.DATA_FILE, backup_file)
            
            # Backup images too
            if os.path.exists(self.IMAGE_DIR) and os.listdir(self.IMAGE_DIR):
                backup_img = os.path.join(self.BACKUP_DIR, f"images_{timestamp}")
                if not os.path.exists(backup_img):
                    shutil.copytree(self.IMAGE_DIR, backup_img)
            
            messagebox.showinfo("Backup Complete", f"Backup saved:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))
    
    def restore_data(self):
        """Restore from a backup file."""
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            initialdir=self.BACKUP_DIR,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path and messagebox.askyesno("Confirm", 
            "This will replace all current data. Continue?"):
            try:
                shutil.copy(file_path, self.DATA_FILE)
                self.load_data()
                self.create_main_menu()
                messagebox.showinfo("Success", "Data restored!")
            except Exception as e:
                messagebox.showerror("Failed", str(e))
    
    def save_image(self, image_path: str) -> str:
        """Save an image to the flashcard images directory."""
        if not image_path or not os.path.exists(image_path):
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(image_path)[1]
            filename = f"img_{timestamp}_{random.randint(1000, 9999)}{ext}"
            dest = os.path.join(self.IMAGE_DIR, filename)
            shutil.copy(image_path, dest)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return ""
    
    def load_image(self, filename: str, max_size=(400, 300)):
        """Load and cache an image."""
        if not filename or not PIL_AVAILABLE:
            return None
        
        cache_key = f"{filename}_{max_size}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            path = os.path.join(self.IMAGE_DIR, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_cache[cache_key] = photo
                return photo
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def delete_image(self, filename: str):
        """Delete an image file."""
        if not filename:
            return
        
        try:
            path = os.path.join(self.IMAGE_DIR, filename)
            if os.path.exists(path):
                os.remove(path)
            
            # Clear from cache
            self.image_cache = {k: v for k, v in self.image_cache.items() 
                               if not k.startswith(filename)}
        except Exception as e:
            print(f"Error deleting image: {e}")
    
    def create_deck(self, deck_name: str, description: str = "") -> bool:
        """Create a new deck."""
        if deck_name in self.data["decks"]:
            return False
        
        self.data["decks"][deck_name] = {
            "cards": [],
            "description": description,
            "created": datetime.now().isoformat(),
            "last_studied": None,
            "stats": {"total_studies": 0, "total_time": 0}
        }
        self.save_data()
        return True
    
    def delete_deck(self, deck_name: str) -> bool:
        """Delete a deck and all its cards."""
        if deck_name not in self.data["decks"]:
            return False
        
        # Delete associated images
        for card in self.data["decks"][deck_name]["cards"]:
            self.delete_image(card.get("question_image", ""))
            self.delete_image(card.get("answer_image", ""))
        
        del self.data["decks"][deck_name]
        if self.data["settings"]["last_used_deck"] == deck_name:
            self.data["settings"]["last_used_deck"] = None
        self.save_data()
        return True
    
    def get_deck_cards(self, deck_name: str) -> List[Dict]:
        """Get all cards from a deck."""
        return self.data["decks"].get(deck_name, {}).get("cards", [])
    
    def add_card_to_deck(self, deck_name: str, question: str, answer: str,
                        q_img: str = "", a_img: str = "", tags: List[str] = None) -> bool:
        """Add a card to a deck."""
        if deck_name not in self.data["decks"]:
            return False
        
        card = {
            "question": question,
            "answer": answer,
            "question_image": q_img,
            "answer_image": a_img,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "review_count": 0
        }
        self.data["decks"][deck_name]["cards"].append(card)
        
        # Update global tags
        if tags:
            for tag in tags:
                if tag not in self.data["tags"]:
                    self.data["tags"].append(tag)
        
        self.save_data()
        return True
    
    def create_main_menu(self):
        """Create the main menu interface."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_menu_bar()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        # Title
        tk.Label(
            main_frame,
            text="📚 Enhanced Flashcard App",
            font=("Arial", 28, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(pady=20)
        
        # Statistics
        deck_count = len(self.data["decks"])
        total_cards = sum(len(d["cards"]) for d in self.data["decks"].values())
        tag_count = len(self.data["tags"])
        
        stats_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        stats_frame.pack(pady=10)
        
        for label, value, color in [
            ("Decks", deck_count, self.colors['accent']),
            ("Cards", total_cards, self.colors['success']),
            ("Tags", tag_count, self.colors['warning'])
        ]:
            sf = tk.Frame(stats_frame, bg=self.colors['card_bg'], relief='raised', bd=2)
            sf.pack(side=tk.LEFT, padx=15)
            
            tk.Label(sf, text=str(value), font=("Arial", 24, "bold"),
                    bg=self.colors['card_bg'], fg=color).pack(padx=20, pady=(10, 0))
            
            tk.Label(sf, text=label, font=("Arial", 11),
                    bg=self.colors['card_bg'], fg=self.colors['fg']).pack(padx=20, pady=(0, 10))
        
        # Search bar
        search_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        search_frame.pack(pady=15)
        
        tk.Label(search_frame, text="🔍", font=("Arial", 16),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame, text="Search",
            command=lambda: self.search_cards(self.search_entry.get()),
            font=("Arial", 10), bg=self.colors['accent'], fg='white',
            relief='flat', padx=15, pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Deck list title
        tk.Label(
            main_frame, text="Your Decks:",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'], fg=self.colors['fg']
        ).pack(pady=(20, 10))
        
        # Scrollable deck list
        list_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        list_frame.pack(fill='both', expand=True, padx=20)
        
        canvas = tk.Canvas(list_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        if not self.data["decks"]:
            tk.Label(scrollable, text="No decks yet. Create your first deck!",
                    font=("Arial", 12), bg=self.colors['bg'],
                    fg=self.colors['fg']).pack(pady=50)
        else:
            for name, data in sorted(self.data["decks"].items()):
                self.create_deck_card(scrollable, name, data)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        for text, cmd, color in [
            ("➕ Create New Deck", self.create_new_deck, self.colors['success']),
            ("📖 Study All Cards", self.study_all_decks, self.colors['warning']),
            ("📊 View Statistics", self.view_study_history, self.colors['accent'])
        ]:
            tk.Button(btn_frame, text=text, command=cmd, width=20,
                     font=("Arial", 11, "bold"), bg=color, fg='white',
                     relief='flat', padx=10, pady=8).pack(side=tk.LEFT, padx=10)
    
    def create_deck_card(self, parent, deck_name: str, deck_data: Dict):
        """Create a visual card for a deck."""
        card_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=2)
        card_frame.pack(pady=8, padx=10, fill='x')
        
        # Header
        header = tk.Frame(card_frame, bg=self.colors['card_bg'])
        header.pack(fill='x', padx=15, pady=10)
        
        tk.Label(header, text=deck_name, font=("Arial", 14, "bold"),
                bg=self.colors['card_bg'], fg=self.colors['fg']).pack(side=tk.LEFT)
        
        card_count = len(deck_data["cards"])
        tk.Label(header, text=f"{card_count} cards", font=("Arial", 9),
                bg=self.colors['accent'], fg='white',
                padx=8, pady=2).pack(side=tk.RIGHT)
        
        # Description
        if deck_data.get("description"):
            tk.Label(card_frame, text=deck_data["description"],
                    font=("Arial", 10), bg=self.colors['card_bg'],
                    fg=self.colors['fg'], wraplength=800,
                    justify='left').pack(padx=15, pady=(0, 10), anchor='w')
        
        # Action buttons
        btn_frame = tk.Frame(card_frame, bg=self.colors['card_bg'])
        btn_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        for text, cmd, color in [
            ("📖 Study", lambda d=deck_name: self.study_deck(d), self.colors['accent']),
            ("📝 Manage", lambda d=deck_name: self.show_deck_management(d), self.colors['success']),
            ("📤 Export", lambda d=deck_name: self.export_deck(d), self.colors['warning']),
            ("🗑️ Delete", lambda d=deck_name: self.delete_deck_confirm(d), self.colors['danger'])
        ]:
            tk.Button(btn_frame, text=text, command=cmd, font=("Arial", 9),
                     bg=color, fg='white', relief='flat',
                     padx=10, pady=4).pack(side=tk.LEFT, padx=5)
    
    def create_new_deck(self):
        """Dialog to create a new deck."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Deck")
        dialog.geometry("450x280")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Create New Deck", font=("Arial", 16, "bold"),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=15)
        
        tk.Label(dialog, text="Deck Name:", font=("Arial", 11),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(10, 5))
        name_entry = tk.Entry(dialog, width=40, font=("Arial", 11))
        name_entry.pack(pady=5)
        name_entry.focus()
        
        tk.Label(dialog, text="Description (optional):", font=("Arial", 11),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(10, 5))
        desc_entry = tk.Entry(dialog, width=40, font=("Arial", 11))
        desc_entry.pack(pady=5)
        
        def create():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Warning", "Please enter a deck name!")
                return
            
            if self.create_deck(name, desc):
                messagebox.showinfo("Success", f"Deck '{name}' created!")
                dialog.destroy()
                self.create_main_menu()
            else:
                messagebox.showerror("Error", f"Deck '{name}' already exists!")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=25)
        
        tk.Button(btn_frame, text="Create", command=create, width=12,
                 font=("Arial", 11), bg=self.colors['success'], fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12,
                 font=("Arial", 11), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        name_entry.bind("<Return>", lambda e: create())
        desc_entry.bind("<Return>", lambda e: create())
    
    def delete_deck_confirm(self, deck_name: str):
        """Confirm and delete a deck."""
        card_count = len(self.get_deck_cards(deck_name))
        
        if messagebox.askyesno("Confirm Delete",
            f"Delete '{deck_name}' with {card_count} cards?\n\nThis cannot be undone!"):
            if self.delete_deck(deck_name):
                messagebox.showinfo("Success", f"Deck '{deck_name}' deleted!")
                self.create_main_menu()
    
    def show_deck_management(self, deck_name: str):
        """Show deck management interface."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_menu_bar()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Button(
            header_frame, text="← Back",
            command=self.create_main_menu,
            font=("Arial", 11), bg=self.colors['button_bg'],
            fg=self.colors['fg'], relief='flat', padx=15, pady=5
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame, text=f"📚 {deck_name}",
            font=("Arial", 20, "bold"),
            bg=self.colors['bg'], fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=20)
        
        # Deck info
        cards = self.get_deck_cards(deck_name)
        deck_data = self.data["decks"][deck_name]
        
        info_frame = tk.Frame(main_frame, bg=self.colors['card_bg'], relief='raised', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = f"📊 {len(cards)} cards"
        if deck_data.get("description"):
            info_text += f" | {deck_data['description']}"
        
        tk.Label(info_frame, text=info_text, font=("Arial", 11),
                bg=self.colors['card_bg'], fg=self.colors['fg'],
                padx=15, pady=10).pack()
        
        # Action buttons
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=15)
        
        for text, cmd, color in [
            ("➕ Add Card", lambda: self.add_card_dialog(deck_name), self.colors['success']),
            ("📝 Edit Cards", lambda: self.edit_deck_cards(deck_name), self.colors['accent']),
            ("📖 View All", lambda: self.view_deck_cards(deck_name), self.colors['warning']),
            ("📚 Study Now", lambda: self.study_deck(deck_name), self.colors['accent'])
        ]:
            tk.Button(btn_frame, text=text, command=cmd,
                     font=("Arial", 11, "bold"), bg=color, fg='white',
                     relief='flat', padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        # Recent cards preview
        if cards:
            tk.Label(main_frame, text="Recent Cards:", font=("Arial", 14, "bold"),
                    bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(20, 10))
            
            cards_frame = tk.Frame(main_frame, bg=self.colors['bg'])
            cards_frame.pack(fill='both', expand=True, padx=20)
            
            canvas = tk.Canvas(cards_frame, bg=self.colors['bg'], highlightthickness=0)
            scrollbar = tk.Scrollbar(cards_frame, command=canvas.yview)
            scrollable = tk.Frame(canvas, bg=self.colors['bg'])
            
            scrollable.bind("<Configure>",
                           lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for i, card in enumerate(cards[:10]):  # Show first 10
                self.create_card_preview(scrollable, card, i, deck_name)
            
            if len(cards) > 10:
                tk.Label(scrollable, text=f"... and {len(cards) - 10} more cards",
                        font=("Arial", 11, "italic"), bg=self.colors['bg'],
                        fg=self.colors['fg']).pack(pady=10)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        else:
            tk.Label(main_frame,
                    text="No cards in this deck yet.\nClick 'Add Card' to get started!",
                    font=("Arial", 13), bg=self.colors['bg'],
                    fg=self.colors['fg']).pack(pady=50)
    
    def create_card_preview(self, parent, card: Dict, index: int, deck_name: str):
        """Create a preview of a card."""
        card_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=1)
        card_frame.pack(pady=5, padx=10, fill='x')
        
        header = tk.Frame(card_frame, bg=self.colors['card_bg'])
        header.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header, text=f"Card #{index + 1}", font=("Arial", 10, "bold"),
                bg=self.colors['card_bg'], fg=self.colors['accent']).pack(side=tk.LEFT)
        
        if card.get("tags"):
            tags_text = " ".join([f"#{tag}" for tag in card["tags"]])
            tk.Label(header, text=tags_text, font=("Arial", 9),
                    bg=self.colors['card_bg'], fg=self.colors['warning']).pack(side=tk.RIGHT)
        
        # Question preview
        q_preview = card["question"][:80] + "..." if len(card["question"]) > 80 else card["question"]
        tk.Label(card_frame, text=f"Q: {q_preview}", font=("Arial", 10),
                bg=self.colors['card_bg'], fg=self.colors['fg'],
                wraplength=800, justify='left').pack(anchor='w', padx=10, pady=2)
        
        # Image indicators
        indicators = []
        if card.get("question_image"):
            indicators.append("🖼️ Q")
        if card.get("answer_image"):
            indicators.append("🖼️ A")
        
        if indicators:
            tk.Label(card_frame, text=" ".join(indicators), font=("Arial", 9),
                    bg=self.colors['card_bg'], fg=self.colors['fg']).pack(anchor='w', padx=10, pady=(0, 5))
    
    def add_card_dialog(self, deck_name: str):
        """Dialog to add a new card with images and tags."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Card to '{deck_name}'")
        dialog.geometry("750x850")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        
        # Variables for images
        question_image_path = tk.StringVar()
        answer_image_path = tk.StringVar()
        
        # Title
        tk.Label(dialog, text=f"Add New Card to '{deck_name}'",
                font=("Arial", 16, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        content_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Question section with RESIZABLE text
        tk.Label(content_frame, text="Question:", font=("Arial", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(10, 5))
        
        question_text = ResizableText(content_frame, height=5, width=70, font=("Arial", 11))
        question_text.pack(pady=5, padx=20, fill='x')
        
        # Question image
        q_img_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        q_img_frame.pack(pady=5)
        
        q_img_label = tk.Label(q_img_frame, text="No image attached",
                              bg=self.colors['bg'], fg=self.colors['fg'])
        q_img_label.pack()
        
        def select_q_image():
            if not PIL_AVAILABLE:
                messagebox.showwarning("Feature Unavailable",
                    "Image support requires Pillow.\nInstall: pip install Pillow")
                return
            
            file_path = filedialog.askopenfilename(
                title="Select Question Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                          ("All files", "*.*")]
            )
            if file_path:
                question_image_path.set(file_path)
                q_img_label.config(text=f"📎 {os.path.basename(file_path)}")
        
        tk.Button(q_img_frame, text="📎 Attach Image", command=select_q_image,
                 font=("Arial", 10), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=10, pady=5).pack(pady=5)
        
        # Answer section with RESIZABLE text
        tk.Label(content_frame, text="Answer:", font=("Arial", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(20, 5))
        
        answer_text = ResizableText(content_frame, height=5, width=70, font=("Arial", 11))
        answer_text.pack(pady=5, padx=20, fill='x')
        
        # Answer image
        a_img_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        a_img_frame.pack(pady=5)
        
        a_img_label = tk.Label(a_img_frame, text="No image attached",
                              bg=self.colors['bg'], fg=self.colors['fg'])
        a_img_label.pack()
        
        def select_a_image():
            if not PIL_AVAILABLE:
                messagebox.showwarning("Feature Unavailable",
                    "Image support requires Pillow.\nInstall: pip install Pillow")
                return
            
            file_path = filedialog.askopenfilename(
                title="Select Answer Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                          ("All files", "*.*")]
            )
            if file_path:
                answer_image_path.set(file_path)
                a_img_label.config(text=f"📎 {os.path.basename(file_path)}")
        
        tk.Button(a_img_frame, text="📎 Attach Image", command=select_a_image,
                 font=("Arial", 10), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=10, pady=5).pack(pady=5)
        
        # Tags section
        tk.Label(content_frame, text="Tags (comma-separated, optional):",
                font=("Arial", 12, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=(20, 5))
        
        tags_entry = tk.Entry(content_frame, width=60, font=("Arial", 11))
        tags_entry.pack(pady=5)
        
        if self.data["tags"]:
            existing_tags = ", ".join(self.data["tags"][:10])
            if len(self.data["tags"]) > 10:
                existing_tags += f", ... ({len(self.data["tags"])} total)"
            
            tk.Label(content_frame, text=f"Existing tags: {existing_tags}",
                    font=("Arial", 9), bg=self.colors['bg'],
                    fg=self.colors['fg']).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=15)
        
        def save_card():
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            
            if not question or not answer:
                messagebox.showwarning("Warning", "Question and answer are required!")
                return
            
            # Save images
            q_img = self.save_image(question_image_path.get())
            a_img = self.save_image(answer_image_path.get())
            
            # Parse tags
            tags = [t.strip() for t in tags_entry.get().split(",") if t.strip()]
            
            if self.add_card_to_deck(deck_name, question, answer, q_img, a_img, tags):
                messagebox.showinfo("Success", "Card added!")
                dialog.destroy()
                self.show_deck_management(deck_name)
            else:
                messagebox.showerror("Error", "Could not add card!")
        
        tk.Button(btn_frame, text="💾 Save Card", command=save_card, width=15,
                 font=("Arial", 11, "bold"), bg=self.colors['success'],
                 fg='white', relief='flat', padx=10, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15,
                 font=("Arial", 11), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=8).pack(side=tk.LEFT, padx=5)
    
    def edit_deck_cards(self, deck_name: str):
        """Edit cards in a deck."""
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("No Cards", "No cards to edit!")
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_menu_bar()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(main_frame, text=f"Edit Cards in '{deck_name}'",
                font=("Arial", 18, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=20)
        
        # List of cards
        list_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(list_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, card in enumerate(cards):
            self.create_editable_card_row(scrollable, deck_name, i, card)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Back button
        tk.Button(main_frame, text="← Back to Deck",
                 command=lambda: self.show_deck_management(deck_name),
                 font=("Arial", 11), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=20, pady=8).pack(pady=15)
    
    def create_editable_card_row(self, parent, deck_name: str, index: int, card: Dict):
        """Create an editable row for a card."""
        row_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=2)
        row_frame.pack(pady=5, padx=10, fill='x')
        
        info_frame = tk.Frame(row_frame, bg=self.colors['card_bg'])
        info_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(info_frame, text=f"#{index + 1}", font=("Arial", 11, "bold"),
                bg=self.colors['card_bg'], fg=self.colors['accent'],
                width=5).pack(side=tk.LEFT)
        
        q_preview = card["question"][:60] + "..." if len(card["question"]) > 60 else card["question"]
        tk.Label(info_frame, text=q_preview, font=("Arial", 10),
                bg=self.colors['card_bg'], fg=self.colors['fg'],
                anchor='w').pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        
        btn_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="✏️ Edit",
                 command=lambda: self.edit_single_card(deck_name, index),
                 font=("Arial", 9), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="🗑️ Delete",
                 command=lambda: self.delete_card(deck_name, index),
                 font=("Arial", 9), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
    
    def edit_single_card(self, deck_name: str, card_index: int):
        """Edit a single card with resizable text areas."""
        cards = self.get_deck_cards(deck_name)
        if card_index >= len(cards):
            messagebox.showerror("Error", "Card not found!")
            return
        
        card = cards[card_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Card #{card_index + 1}")
        dialog.geometry("750x850")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        
        # Variables
        question_image_path = tk.StringVar(value=card.get("question_image", ""))
        answer_image_path = tk.StringVar(value=card.get("answer_image", ""))
        
        tk.Label(dialog, text=f"Edit Card #{card_index + 1} in '{deck_name}'",
                font=("Arial", 16, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        content_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Question with RESIZABLE text
        tk.Label(content_frame, text="Question:", font=("Arial", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(10, 5))
        
        question_text = ResizableText(content_frame, height=5, width=70, font=("Arial", 11))
        question_text.pack(pady=5, padx=20, fill='x')
        question_text.insert("1.0", card["question"])
        
        # Question image management
        q_img_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        q_img_frame.pack(pady=5)
        
        q_img_status = "No image" if not card.get("question_image") else f"📎 {card['question_image']}"
        q_img_label = tk.Label(q_img_frame, text=q_img_status,
                              bg=self.colors['bg'], fg=self.colors['fg'])
        q_img_label.pack()
        
        def select_q_image():
            if not PIL_AVAILABLE:
                messagebox.showwarning("Feature Unavailable",
                    "Image support requires Pillow.\nInstall: pip install Pillow")
                return
            
            file_path = filedialog.askopenfilename(
                title="Select Question Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                          ("All files", "*.*")]
            )
            if file_path:
                question_image_path.set(file_path)
                q_img_label.config(text=f"📎 {os.path.basename(file_path)}")
        
        def remove_q_image():
            question_image_path.set("")
            q_img_label.config(text="No image")
        
        btn_row = tk.Frame(q_img_frame, bg=self.colors['bg'])
        btn_row.pack(pady=5)
        
        tk.Button(btn_row, text="📎 Change Image", command=select_q_image,
                 font=("Arial", 9), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_row, text="✕ Remove", command=remove_q_image,
                 font=("Arial", 9), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
        
        # Answer with RESIZABLE text
        tk.Label(content_frame, text="Answer:", font=("Arial", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=(20, 5))
        
        answer_text = ResizableText(content_frame, height=5, width=70, font=("Arial", 11))
        answer_text.pack(pady=5, padx=20, fill='x')
        answer_text.insert("1.0", card["answer"])
        
        # Answer image management
        a_img_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        a_img_frame.pack(pady=5)
        
        a_img_status = "No image" if not card.get("answer_image") else f"📎 {card['answer_image']}"
        a_img_label = tk.Label(a_img_frame, text=a_img_status,
                              bg=self.colors['bg'], fg=self.colors['fg'])
        a_img_label.pack()
        
        def select_a_image():
            if not PIL_AVAILABLE:
                messagebox.showwarning("Feature Unavailable",
                    "Image support requires Pillow.\nInstall: pip install Pillow")
                return
            
            file_path = filedialog.askopenfilename(
                title="Select Answer Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                          ("All files", "*.*")]
            )
            if file_path:
                answer_image_path.set(file_path)
                a_img_label.config(text=f"📎 {os.path.basename(file_path)}")
        
        def remove_a_image():
            answer_image_path.set("")
            a_img_label.config(text="No image")
        
        btn_row2 = tk.Frame(a_img_frame, bg=self.colors['bg'])
        btn_row2.pack(pady=5)
        
        tk.Button(btn_row2, text="📎 Change Image", command=select_a_image,
                 font=("Arial", 9), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_row2, text="✕ Remove", command=remove_a_image,
                 font=("Arial", 9), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=4).pack(side=tk.LEFT, padx=3)
        
        # Tags
        tk.Label(content_frame, text="Tags (comma-separated):",
                font=("Arial", 12, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=(20, 5))
        
        tags_entry = tk.Entry(content_frame, width=60, font=("Arial", 11))
        tags_entry.pack(pady=5)
        if card.get("tags"):
            tags_entry.insert(0, ", ".join(card["tags"]))
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
        
        # Save/Cancel buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=15)
        
        def save_changes():
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            
            if not question or not answer:
                messagebox.showwarning("Warning", "Question and answer are required!")
                return
            
            # Handle images
            q_img = question_image_path.get()
            if q_img and q_img != card.get("question_image", ""):
                if os.path.exists(q_img):  # New image
                    q_img = self.save_image(q_img)
                    if card.get("question_image"):
                        self.delete_image(card["question_image"])
            elif not q_img:  # Remove image
                if card.get("question_image"):
                    self.delete_image(card["question_image"])
            else:  # Keep existing
                q_img = card.get("question_image", "")
            
            a_img = answer_image_path.get()
            if a_img and a_img != card.get("answer_image", ""):
                if os.path.exists(a_img):
                    a_img = self.save_image(a_img)
                    if card.get("answer_image"):
                        self.delete_image(card["answer_image"])
            elif not a_img:
                if card.get("answer_image"):
                    self.delete_image(card["answer_image"])
            else:
                a_img = card.get("answer_image", "")
            
            # Parse tags
            tags = [t.strip() for t in tags_entry.get().split(",") if t.strip()]
            
            # Update card
            self.data["decks"][deck_name]["cards"][card_index].update({
                "question": question,
                "answer": answer,
                "question_image": q_img,
                "answer_image": a_img,
                "tags": tags
            })
            
            # Update global tags
            for tag in tags:
                if tag not in self.data["tags"]:
                    self.data["tags"].append(tag)
            
            self.save_data()
            messagebox.showinfo("Success", "Card updated!")
            dialog.destroy()
            self.edit_deck_cards(deck_name)
        
        tk.Button(btn_frame, text="💾 Save Changes", command=save_changes, width=15,
                 font=("Arial", 11, "bold"), bg=self.colors['success'],
                 fg='white', relief='flat', padx=10, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15,
                 font=("Arial", 11), bg=self.colors['danger'], fg='white',
                 relief='flat', padx=10, pady=8).pack(side=tk.LEFT, padx=5)
    
    def delete_card(self, deck_name: str, card_index: int):
        """Delete a card."""
        if messagebox.askyesno("Confirm", "Delete this card?"):
            cards = self.get_deck_cards(deck_name)
            if card_index < len(cards):
                card = cards[card_index]
                
                # Delete images
                self.delete_image(card.get("question_image", ""))
                self.delete_image(card.get("answer_image", ""))
                
                del self.data["decks"][deck_name]["cards"][card_index]
                self.save_data()
                messagebox.showinfo("Success", "Card deleted!")
                self.edit_deck_cards(deck_name)
    
    def view_deck_cards(self, deck_name: str):
        """View all cards in a deck."""
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("No Cards", "No cards to display!")
            return
        
        view_window = tk.Toplevel(self.root)
        view_window.title(f"All Cards in '{deck_name}'")
        view_window.geometry("900x750")
        view_window.configure(bg=self.colors['bg'])
        
        tk.Label(view_window, text=f"📖 {deck_name} - All Cards ({len(cards)} total)",
                font=("Arial", 16, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        # Scrollable frame
        canvas = tk.Canvas(view_window, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display cards
        for i, card in enumerate(cards):
            card_frame = tk.Frame(scrollable, bg=self.colors['card_bg'],
                                 relief='raised', bd=2)
            card_frame.pack(pady=10, padx=20, fill='x')
            
            tk.Label(card_frame, text=f"Card #{i+1}", font=("Arial", 12, "bold"),
                    bg=self.colors['card_bg'], fg=self.colors['accent']).pack(pady=10)
            
            # Tags
            if card.get("tags"):
                tags_frame = tk.Frame(card_frame, bg=self.colors['card_bg'])
                tags_frame.pack()
                
                for tag in card["tags"]:
                    tk.Label(tags_frame, text=f"#{tag}", font=("Arial", 8),
                            bg=self.colors['warning'], fg='white',
                            padx=6, pady=2).pack(side=tk.LEFT, padx=2)
            
            # Question
            tk.Label(card_frame, text="Q:", font=("Arial", 10, "bold"),
                    bg=self.colors['card_bg'], fg=self.colors['fg']).pack(anchor='w', padx=15, pady=(10, 5))
            
            tk.Label(card_frame, text=card["question"], font=("Arial", 10),
                    bg=self.colors['card_bg'], fg=self.colors['fg'],
                    wraplength=800, justify='left').pack(anchor='w', padx=30, pady=2)
            
            # Question image
            if card.get("question_image"):
                q_img = self.load_image(card["question_image"], max_size=(350, 250))
                if q_img:
                    lbl = tk.Label(card_frame, image=q_img, bg=self.colors['card_bg'])
                    lbl.image = q_img
                    lbl.pack(pady=5)
            
            # Answer
            tk.Label(card_frame, text="A:", font=("Arial", 10, "bold"),
                    bg=self.colors['card_bg'], fg=self.colors['fg']).pack(anchor='w', padx=15, pady=(10, 5))
            
            tk.Label(card_frame, text=card["answer"], font=("Arial", 10),
                    bg=self.colors['card_bg'], fg=self.colors['fg'],
                    wraplength=800, justify='left').pack(anchor='w', padx=30, pady=2)
            
            # Answer image
            if card.get("answer_image"):
                a_img = self.load_image(card["answer_image"], max_size=(350, 250))
                if a_img:
                    lbl = tk.Label(card_frame, image=a_img, bg=self.colors['card_bg'])
                    lbl.image = a_img
                    lbl.pack(pady=5)
            
            tk.Label(card_frame, text="", bg=self.colors['card_bg']).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(view_window, text="Close", command=view_window.destroy,
                 font=("Arial", 11), bg=self.colors['accent'], fg='white',
                 relief='flat', padx=20, pady=8).pack(pady=15)
    
    def study_deck(self, deck_name: str):
        """Start studying a specific deck."""
        self.current_deck = deck_name
        self.study_cards = self.get_deck_cards(deck_name).copy()
        
        if not self.study_cards:
            messagebox.showinfo("No Cards", "This deck has no cards!")
            return
        
        self.start_study_session()
    
    def study_all_decks(self):
        """Study cards from all decks."""
        all_cards = []
        for deck_name, deck_data in self.data["decks"].items():
            for card in deck_data["cards"]:
                card_copy = card.copy()
                card_copy["deck"] = deck_name
                all_cards.append(card_copy)
        
        if not all_cards:
            messagebox.showinfo("No Cards", "No cards available!")
            return
        
        self.current_deck = None
        self.study_cards = all_cards
        self.start_study_session()
    
    def start_study_session(self):
        """Initialize a study session."""
        self.current_card_index = 0
        self.known_cards = set()
        self.show_answer = False
        self.session_start_time = datetime.now()
        
        # Shuffle cards randomly
        if random.random() < 0.5:
            random.shuffle(self.study_cards)
        
        self.show_study_card()
    
    def show_study_card(self):
        """Display the current study card."""
        if self.current_card_index >= len(self.study_cards):
            self.finish_study_session()
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_menu_bar()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        # Progress
        progress_text = f"Card {self.current_card_index + 1} of {len(self.study_cards)}"
        if self.current_deck:
            progress_text = f"{self.current_deck} | {progress_text}"
        
        tk.Label(main_frame, text=progress_text, font=("Arial", 13),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)
        
        progress = ((self.current_card_index + 1) / len(self.study_cards)) * 100
        progress_bar = ttk.Progressbar(main_frame, length=600, value=progress)
        progress_bar.pack(pady=5)
        
        # Card content
        card = self.study_cards[self.current_card_index]
        
        card_frame = tk.Frame(main_frame, bg=self.colors['card_bg'],
                             relief='raised', bd=3)
        card_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        # Question
        tk.Label(card_frame, text="Question:", font=("Arial", 13, "bold"),
                bg=self.colors['card_bg'], fg=self.colors['accent']).pack(pady=(20, 10))
        
        tk.Label(card_frame, text=card["question"], font=("Arial", 14),
                bg=self.colors['card_bg'], fg=self.colors['fg'],
                wraplength=700, justify='center').pack(pady=10, padx=30)
        
        # Question image
        if card.get("question_image"):
            q_img = self.load_image(card["question_image"])
            if q_img:
                lbl = tk.Label(card_frame, image=q_img, bg=self.colors['card_bg'])
                lbl.image = q_img
                lbl.pack(pady=10)
        
        # Answer (if revealed)
        if self.show_answer:
            tk.Frame(card_frame, height=2, bg=self.colors['accent']).pack(fill='x', pady=20, padx=30)
            
            tk.Label(card_frame, text="Answer:", font=("Arial", 13, "bold"),
                    bg=self.colors['card_bg'], fg=self.colors['success']).pack(pady=10)
            
            tk.Label(card_frame, text=card["answer"], font=("Arial", 14),
                    bg=self.colors['card_bg'], fg=self.colors['fg'],
                    wraplength=700, justify='center').pack(pady=10, padx=30)
            
            # Answer image
            if card.get("answer_image"):
                a_img = self.load_image(card["answer_image"])
                if a_img:
                    lbl = tk.Label(card_frame, image=a_img, bg=self.colors['card_bg'])
                    lbl.image = a_img
                    lbl.pack(pady=10)
        
        # Tags
        if card.get("tags"):
            tags_frame = tk.Frame(card_frame, bg=self.colors['card_bg'])
            tags_frame.pack(pady=10)
            
            for tag in card["tags"]:
                tk.Label(tags_frame, text=f"#{tag}", font=("Arial", 9),
                        bg=self.colors['warning'], fg='white',
                        padx=8, pady=3).pack(side=tk.LEFT, padx=3)
        
        # Controls
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        if not self.show_answer:
            tk.Button(btn_frame, text="👁️ Show Answer",
                     command=self.toggle_answer, width=20,
                     font=("Arial", 12, "bold"), bg=self.colors['accent'],
                     fg='white', relief='flat', padx=15, pady=10).pack()
        else:
            tk.Label(btn_frame, text="How well did you know this?",
                    font=("Arial", 11), bg=self.colors['bg'],
                    fg=self.colors['fg']).pack(pady=(0, 10))
            
            buttons = tk.Frame(btn_frame, bg=self.colors['bg'])
            buttons.pack()
            
            tk.Button(buttons, text="❌ Didn't Know",
                     command=lambda: self.next_card(False), width=18,
                     font=("Arial", 11, "bold"), bg=self.colors['danger'],
                     fg='white', relief='flat', padx=15, pady=10).pack(side=tk.LEFT, padx=10)
            
            tk.Button(buttons, text="✓ Knew It",
                     command=lambda: self.next_card(True), width=18,
                     font=("Arial", 11, "bold"), bg=self.colors['success'],
                     fg='white', relief='flat', padx=15, pady=10).pack(side=tk.LEFT, padx=10)
        
        # End session button
        tk.Button(main_frame, text="⏸️ End Session",
                 command=self.finish_study_session, font=("Arial", 10),
                 bg=self.colors['button_bg'], fg=self.colors['fg'],
                 relief='flat', padx=15, pady=5).pack(pady=10)
        
        # Keyboard shortcuts
        self.root.bind("<space>", lambda e: self.toggle_answer() if not self.show_answer else None)
        self.root.bind("<Right>", lambda e: self.next_card(True) if self.show_answer else None)
        self.root.bind("<Left>", lambda e: self.next_card(False) if self.show_answer else None)
    
    def toggle_answer(self):
        """Toggle answer visibility."""
        self.show_answer = True
        self.show_study_card()
    
    def next_card(self, knew_it: bool):
        """Move to next card."""
        if knew_it:
            self.known_cards.add(self.current_card_index)
        
        self.current_card_index += 1
        self.show_answer = False
        self.show_study_card()
    
    def finish_study_session(self):
        """End study session and show results."""
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds()
            studied = self.current_card_index
            known = len(self.known_cards)
            
            # Save to history
            self.data["study_history"].append({
                "date": datetime.now().isoformat(),
                "deck": self.current_deck or "All Decks",
                "cards_studied": studied,
                "cards_known": known,
                "duration": duration
            })
            
            # Update deck stats
            if self.current_deck and self.current_deck in self.data["decks"]:
                self.data["decks"][self.current_deck]["last_studied"] = datetime.now().isoformat()
                self.data["decks"][self.current_deck]["stats"]["total_studies"] += 1
                self.data["decks"][self.current_deck]["stats"]["total_time"] += duration
            
            self.save_data()
            
            # Show results
            accuracy = (known / studied * 100) if studied > 0 else 0
            
            messagebox.showinfo(
                "Study Session Complete! 🎉",
                f"Great work!\n\n"
                f"Cards studied: {studied}\n"
                f"Cards known: {known}\n"
                f"Accuracy: {accuracy:.1f}%\n"
                f"Time: {duration / 60:.1f} minutes"
            )
        
        self.create_main_menu()
    
    def search_cards(self, query: str = ""):
        """Search for cards."""
        if not query:
            query = simpledialog.askstring("Search", "Enter search query:")
        
        if not query:
            return
        
        query = query.lower()
        results = []
        
        for deck_name, deck_data in self.data["decks"].items():
            for i, card in enumerate(deck_data["cards"]):
                if (query in card["question"].lower() or
                    query in card["answer"].lower() or
                    any(query in tag.lower() for tag in card.get("tags", []))):
                    results.append((deck_name, i, card))
        
        if not results:
            messagebox.showinfo("No Results", f"No cards found matching '{query}'")
            return
        
        # Show results
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Search Results")
        result_window.geometry("800x600")
        result_window.configure(bg=self.colors['bg'])
        
        tk.Label(result_window, text=f"Found {len(results)} cards matching '{query}'",
                font=("Arial", 14, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        # Results list
        canvas = tk.Canvas(result_window, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(result_window, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for deck_name, _, card in results:
            result_frame = tk.Frame(scrollable, bg=self.colors['card_bg'],
                                   relief='raised', bd=1)
            result_frame.pack(pady=5, padx=15, fill='x')
            
            tk.Label(result_frame, text=f"📚 {deck_name}",
                    font=("Arial", 10, "bold"), bg=self.colors['card_bg'],
                    fg=self.colors['accent']).pack(anchor='w', padx=10, pady=(5, 2))
            
            q_preview = card["question"][:100] + "..." if len(card["question"]) > 100 else card["question"]
            tk.Label(result_frame, text=f"Q: {q_preview}",
                    font=("Arial", 9), bg=self.colors['card_bg'],
                    fg=self.colors['fg'], wraplength=700,
                    justify='left').pack(anchor='w', padx=20, pady=2)
            
            tk.Button(result_frame, text="View in Deck",
                     command=lambda d=deck_name: (result_window.destroy(), self.show_deck_management(d)),
                     font=("Arial", 8), bg=self.colors['accent'],
                     fg='white', relief='flat', padx=8,
                     pady=3).pack(anchor='e', padx=10, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(result_window, text="Close", command=result_window.destroy,
                 font=("Arial", 10), bg=self.colors['button_bg'],
                 fg=self.colors['fg'], relief='flat',
                 padx=15, pady=5).pack(pady=10)
    
    def view_all_tags(self):
        """View all tags."""
        if not self.data["tags"]:
            messagebox.showinfo("No Tags", "No tags created yet!")
            return
        
        tag_window = tk.Toplevel(self.root)
        tag_window.title("All Tags")
        tag_window.geometry("500x400")
        tag_window.configure(bg=self.colors['bg'])
        
        tk.Label(tag_window, text=f"All Tags ({len(self.data['tags'])})",
                font=("Arial", 14, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        canvas = tk.Canvas(tag_window, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(tag_window, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for tag in sorted(self.data["tags"]):
            count = 0
            for deck_data in self.data["decks"].values():
                count += sum(1 for card in deck_data["cards"]
                           if tag in card.get("tags", []))
            
            tag_frame = tk.Frame(scrollable, bg=self.colors['card_bg'],
                                relief='raised', bd=1)
            tag_frame.pack(pady=3, padx=15, fill='x')
            
            tk.Label(tag_frame, text=f"#{tag}", font=("Arial", 11),
                    bg=self.colors['warning'], fg='white',
                    padx=10, pady=5).pack(side=tk.LEFT, padx=10, pady=5)
            
            tk.Label(tag_frame, text=f"{count} cards", font=("Arial", 10),
                    bg=self.colors['card_bg'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=10)
            
            tk.Button(tag_frame, text="Search", command=lambda t=tag: self.search_cards(t),
                     font=("Arial", 9), bg=self.colors['accent'], fg='white',
                     relief='flat', padx=10, pady=3).pack(side=tk.RIGHT, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(tag_window, text="Close", command=tag_window.destroy,
                 font=("Arial", 10), bg=self.colors['button_bg'],
                 fg=self.colors['fg'], relief='flat',
                 padx=15, pady=5).pack(pady=10)
    
    def view_study_history(self):
        """View study session history."""
        if not self.data.get("study_history"):
            messagebox.showinfo("No History", "No study sessions yet!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Study History")
        history_window.geometry("700x500")
        history_window.configure(bg=self.colors['bg'])
        
        tk.Label(history_window,
                text=f"Study History ({len(self.data['study_history'])} sessions)",
                font=("Arial", 14, "bold"), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=15)
        
        # Stats
        total_cards = sum(s["cards_studied"] for s in self.data["study_history"])
        total_time = sum(s["duration"] for s in self.data["study_history"])
        
        if len(self.data["study_history"]) > 0:
            avg_accuracy = sum(
                s["cards_known"] / s["cards_studied"] * 100
                for s in self.data["study_history"] if s["cards_studied"] > 0
            ) / len(self.data["study_history"])
        else:
            avg_accuracy = 0
        
        stats_frame = tk.Frame(history_window, bg=self.colors['card_bg'],
                              relief='raised', bd=2)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        stats_text = (
            f"Total Cards: {total_cards} | "
            f"Total Time: {total_time / 3600:.1f}h | "
            f"Avg Accuracy: {avg_accuracy:.1f}%"
        )
        
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10),
                bg=self.colors['card_bg'], fg=self.colors['fg'],
                padx=15, pady=10).pack()
        
        # History list
        canvas = tk.Canvas(history_window, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(history_window, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for session in reversed(self.data["study_history"][-50:]):
            try:
                date = datetime.fromisoformat(session["date"]).strftime("%Y-%m-%d %H:%M")
            except:
                date = "Unknown"
            
            accuracy = (session["cards_known"] / session["cards_studied"] * 100
                       if session["cards_studied"] > 0 else 0)
            duration_min = session["duration"] / 60
            
            info_text = (
                f"{date} | {session['deck']} | "
                f"{session['cards_studied']} cards | "
                f"{accuracy:.0f}% | {duration_min:.1f} min"
            )
            
            session_frame = tk.Frame(scrollable, bg=self.colors['card_bg'],
                                    relief='raised', bd=1)
            session_frame.pack(pady=3, padx=15, fill='x')
            
            tk.Label(session_frame, text=info_text, font=("Arial", 9),
                    bg=self.colors['card_bg'], fg=self.colors['fg'],
                    padx=10, pady=8).pack(anchor='w')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(history_window, text="Close", command=history_window.destroy,
                 font=("Arial", 10), bg=self.colors['button_bg'],
                 fg=self.colors['fg'], relief='flat',
                 padx=15, pady=5).pack(pady=10)
    
    def export_deck(self, deck_name: str):
        """Export a deck to JSON."""
        if deck_name not in self.data["decks"]:
            messagebox.showerror("Error", "Deck not found!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Deck",
            defaultextension=".json",
            initialfile=f"{deck_name}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = {
                    "deck_name": deck_name,
                    "deck_data": self.data["decks"][deck_name],
                    "exported_at": datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Deck exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))
    
    def import_deck(self):
        """Import a deck from JSON."""
        file_path = filedialog.askopenfilename(
            title="Import Deck",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                deck_name = import_data.get("deck_name")
                deck_data = import_data.get("deck_data")
                
                if not deck_name or not deck_data:
                    messagebox.showerror("Invalid File", "Not a valid deck export!")
                    return
                
                # Handle duplicate names
                original_name = deck_name
                counter = 1
                while deck_name in self.data["decks"]:
                    deck_name = f"{original_name} ({counter})"
                    counter += 1
                
                self.data["decks"][deck_name] = deck_data
                self.save_data()
                
                messagebox.showinfo("Success",
                    f"Imported deck '{deck_name}' with {len(deck_data['cards'])} cards!")
                self.create_main_menu()
            except Exception as e:
                messagebox.showerror("Import Failed", str(e))
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts_text = """
Keyboard Shortcuts

During Study Session:
• Space - Show/Hide answer
• Right Arrow (→) - Mark as "Knew It"
• Left Arrow (←) - Mark as "Didn't Know"

Tips:
• Drag the resize handle (⋮⋮⋮) on text boxes to make them bigger or smaller
• Use tags to organize your cards across decks
• Search works across all decks and tags
• Enable Dark Mode from View menu for night studying
        """
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
Enhanced Flashcard App v2.0

NEW FEATURES:
✨ Image attachments on questions and answers
✨ Resizable text input areas
✨ Dark/Light theme toggle
✨ Card tagging system
✨ Search functionality
✨ Study session history
✨ Backup and restore

Created with Python & Tkinter
Powered by Pillow for image support

All your original features are preserved!
        """
        
        messagebox.showinfo("About", about_text)
    
    def run(self):
        """Start the application."""
        print("=" * 60)
        print("Enhanced Flashcard App with Images & Resizable Text")
        print("=" * 60)
        print(f"Data file: {self.DATA_FILE}")
        print(f"Image directory: {self.IMAGE_DIR}")
        
        if not PIL_AVAILABLE:
            print("\n⚠️  Image features disabled (Pillow not installed)")
        
        deck_count = len(self.data["decks"])
        total_cards = sum(len(d["cards"]) for d in self.data["decks"].values())
        print(f"Loaded {deck_count} decks with {total_cards} cards\n")
        
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.save_data()
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()


def main():
    """Main function."""
    app = FlashcardApp()
    app.run()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
