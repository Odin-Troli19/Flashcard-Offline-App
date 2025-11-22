#!/usr/bin/env python3
"""
Offline Flashcard App with Deck Organization
===========================================

A comprehensive flashcard application that allows you to:
- Create and manage multiple decks (subjects/topics)
- Add, edit, and delete flashcards within each deck
- Study flashcards in order or random mode per deck
- Import/export individual decks
- Save all data locally in JSON format

Requirements: Python 3.x with tkinter (usually included by default)
Data Storage: flashcards_data.json (created automatically in the same directory)

How to use:
1. Run this script: python flashcard_app.py
2. Create decks for different subjects (e.g., "Spanish", "History", "Math")
3. Add flashcards to specific decks
4. Study individual decks or all cards together
5. Data is automatically saved to flashcards_data.json

Customization:
- Modify DATA_FILE to change the data file location
- Adjust window sizes by changing the geometry() values
- Modify colors and fonts in the style configurations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import random
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class FlashcardApp:
    def __init__(self):
        """Initialize the flashcard application with deck support."""
        # Configuration
        self.DATA_FILE = "flashcards_data.json"  # Change this to store data elsewhere
        
        # Data storage - now organized by decks
        self.data = {
            "decks": {},  # deck_name: {"cards": [...], "created": "date", "stats": {...}}
            "settings": {"last_used_deck": None}
        }
        self.current_deck = None
        self.current_card_index = 0
        self.study_mode = "sequential"  # or "random"
        self.shuffled_indices = []
        self.show_answer = False
        self.study_cards = []  # Dynamic list of cards for current study session
        self.known_cards = set()  # Track cards marked as "known" in current session
        
        # Load existing data
        self.load_data()
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Offline Flashcard App - Deck Organizer")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create the main interface
        self.create_main_menu()
    
    def load_data(self) -> None:
        """Load all flashcard data from the JSON file."""
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                # Ensure data structure is correct
                if "decks" not in self.data:
                    self.data["decks"] = {}
                if "settings" not in self.data:
                    self.data["settings"] = {"last_used_deck": None}
                
                deck_count = len(self.data["decks"])
                total_cards = sum(len(deck["cards"]) for deck in self.data["decks"].values())
                print(f"Loaded {deck_count} decks with {total_cards} total cards from {self.DATA_FILE}")
            else:
                self.data = {"decks": {}, "settings": {"last_used_deck": None}}
                print(f"No existing data file found. Starting with empty collection.")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {"decks": {}, "settings": {"last_used_deck": None}}
    
    def save_data(self) -> None:
        """Save all flashcard data to the JSON file."""
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            deck_count = len(self.data["decks"])
            total_cards = sum(len(deck["cards"]) for deck in self.data["decks"].values())
            print(f"Saved {deck_count} decks with {total_cards} total cards to {self.DATA_FILE}")
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Error", f"Could not save data: {e}")
    
    def create_deck(self, deck_name: str) -> bool:
        """Create a new deck."""
        if deck_name in self.data["decks"]:
            return False
        
        self.data["decks"][deck_name] = {
            "cards": [],
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
        
        del self.data["decks"][deck_name]
        if self.data["settings"]["last_used_deck"] == deck_name:
            self.data["settings"]["last_used_deck"] = None
        self.save_data()
        return True
    
    def get_deck_cards(self, deck_name: str) -> List[Dict[str, str]]:
        """Get all cards from a specific deck."""
        if deck_name not in self.data["decks"]:
            return []
        return self.data["decks"][deck_name]["cards"]
    
    def add_card_to_deck(self, deck_name: str, question: str, answer: str) -> bool:
        """Add a card to a specific deck."""
        if deck_name not in self.data["decks"]:
            return False
        
        new_card = {
            "question": question,
            "answer": answer,
            "created": datetime.now().isoformat()
        }
        self.data["decks"][deck_name]["cards"].append(new_card)
        self.save_data()
        return True
    
    def create_main_menu(self) -> None:
        """Create the main menu interface with deck overview."""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="📚 Flashcard App - Deck Manager", 
            font=("Arial", 24, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=20)
        
        # Stats
        deck_count = len(self.data["decks"])
        total_cards = sum(len(deck["cards"]) for deck in self.data["decks"].values())
        stats_text = f"Total Decks: {deck_count} | Total Cards: {total_cards}"
        stats_label = tk.Label(
            self.root, 
            text=stats_text, 
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        stats_label.pack(pady=10)
        
        # Deck management section
        deck_frame = tk.Frame(self.root, bg='#f0f0f0')
        deck_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Deck list title
        tk.Label(
            deck_frame, 
            text="Your Decks:", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        ).pack(pady=(0, 10))
        
        # Scrollable deck list
        list_frame = tk.Frame(deck_frame, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.deck_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            height=10
        )
        self.deck_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.deck_listbox.yview)
        
        # Populate deck list
        self.refresh_deck_list()
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Main action buttons
        buttons_row1 = [
            ("Create New Deck", self.create_new_deck, '#4CAF50'),
            ("Open Selected Deck", self.open_selected_deck, '#2196F3'),
            ("Study Selected Deck", self.study_selected_deck, '#FF9800')
        ]
        
        for text, command, color in buttons_row1:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                width=18,
                height=2,
                font=("Arial", 10),
                bg=color,
                fg='white',
                relief='raised',
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Second row of buttons
        button_frame2 = tk.Frame(self.root, bg='#f0f0f0')
        button_frame2.pack(pady=5)
        
        buttons_row2 = [
            ("Rename Deck", self.rename_selected_deck, '#9C27B0'),
            ("Delete Deck", self.delete_selected_deck, '#f44336'),
            ("Export Deck", self.export_selected_deck, '#607D8B'),
            ("Import Deck", self.import_deck, '#795548')
        ]
        
        for text, command, color in buttons_row2:
            btn = tk.Button(
                button_frame2,
                text=text,
                command=command,
                width=18,
                height=1,
                font=("Arial", 10),
                bg=color,
                fg='white',
                relief='raised',
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_frame = tk.Frame(self.root, bg='#f0f0f0')
        exit_frame.pack(pady=10)
        
        exit_btn = tk.Button(
            exit_frame,
            text="Exit App",
            command=self.root.quit,
            width=15,
            height=1,
            font=("Arial", 10),
            bg='#424242',
            fg='white'
        )
        exit_btn.pack()
    
    def refresh_deck_list(self) -> None:
        """Refresh the deck listbox with current decks."""
        self.deck_listbox.delete(0, tk.END)
        
        if not self.data["decks"]:
            self.deck_listbox.insert(tk.END, "No decks created yet. Click 'Create New Deck' to start!")
            return
        
        for deck_name, deck_data in self.data["decks"].items():
            card_count = len(deck_data["cards"])
            last_studied = "Never"
            if deck_data.get("last_studied"):
                try:
                    date_obj = datetime.fromisoformat(deck_data["last_studied"])
                    last_studied = date_obj.strftime("%Y-%m-%d")
                except:
                    pass
            
            display_text = f"{deck_name} ({card_count} cards) - Last studied: {last_studied}"
            self.deck_listbox.insert(tk.END, display_text)
    
    def create_new_deck(self) -> None:
        """Create a new deck."""
        deck_name = simpledialog.askstring(
            "New Deck", 
            "Enter deck name:",
            parent=self.root
        )
        
        if not deck_name:
            return
        
        deck_name = deck_name.strip()
        if not deck_name:
            messagebox.showwarning("Warning", "Deck name cannot be empty!")
            return
        
        if self.create_deck(deck_name):
            self.refresh_deck_list()
        else:
            messagebox.showerror("Error", f"Deck '{deck_name}' already exists!")
    
    def get_selected_deck_name(self) -> Optional[str]:
        """Get the currently selected deck name."""
        selection = self.deck_listbox.curselection()
        if not selection or not self.data["decks"]:
            return None
        
        deck_names = list(self.data["decks"].keys())
        return deck_names[selection[0]]
    
    def open_selected_deck(self) -> None:
        """Open the selected deck for management."""
        deck_name = self.get_selected_deck_name()
        if not deck_name:
            messagebox.showwarning("Warning", "Please select a deck to open!")
            return
        
        self.current_deck = deck_name
        self.data["settings"]["last_used_deck"] = deck_name
        self.save_data()
        self.show_deck_management(deck_name)
    
    def study_selected_deck(self) -> None:
        """Start studying the selected deck."""
        deck_name = self.get_selected_deck_name()
        if not deck_name:
            messagebox.showwarning("Warning", "Please select a deck to study!")
            return
        
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("Empty Deck", f"Deck '{deck_name}' has no cards to study!")
            return
        
        self.current_deck = deck_name
        self.study_mode_selection()
    
    def rename_selected_deck(self) -> None:
        """Rename the selected deck."""
        old_name = self.get_selected_deck_name()
        if not old_name:
            messagebox.showwarning("Warning", "Please select a deck to rename!")
            return
        
        new_name = simpledialog.askstring(
            "Rename Deck", 
            f"Enter new name for '{old_name}':",
            initialvalue=old_name,
            parent=self.root
        )
        
        if not new_name or new_name.strip() == old_name:
            return
        
        new_name = new_name.strip()
        if new_name in self.data["decks"]:
            messagebox.showerror("Error", f"Deck '{new_name}' already exists!")
            return
        
        # Rename the deck
        self.data["decks"][new_name] = self.data["decks"].pop(old_name)
        if self.data["settings"]["last_used_deck"] == old_name:
            self.data["settings"]["last_used_deck"] = new_name
        
        self.save_data()
        messagebox.showinfo("Success", f"Deck renamed to '{new_name}'!")
        self.refresh_deck_list()
    
    def delete_selected_deck(self) -> None:
        """Delete the selected deck."""
        deck_name = self.get_selected_deck_name()
        if not deck_name:
            messagebox.showwarning("Warning", "Please select a deck to delete!")
            return
        
        card_count = len(self.get_deck_cards(deck_name))
        if not messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete deck '{deck_name}'?\n"
            f"This will permanently remove {card_count} cards!"
        ):
            return
        
        if self.delete_deck(deck_name):
            messagebox.showinfo("Success", f"Deck '{deck_name}' deleted successfully!")
            self.refresh_deck_list()
    
    def export_selected_deck(self) -> None:
        """Export the selected deck to a JSON file."""
        deck_name = self.get_selected_deck_name()
        if not deck_name:
            messagebox.showwarning("Warning", "Please select a deck to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            title=f"Export Deck: {deck_name}",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialvalue=f"{deck_name.replace(' ', '_')}_deck.json"
        )
        
        if not filename:
            return
        
        try:
            export_data = {
                "deck_name": deck_name,
                "exported_date": datetime.now().isoformat(),
                "deck_data": self.data["decks"][deck_name]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Deck '{deck_name}' exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export deck: {e}")
    
    def import_deck(self) -> None:
        """Import a deck from a JSON file."""
        filename = filedialog.askopenfilename(
            title="Import Deck",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "deck_name" not in import_data or "deck_data" not in import_data:
                messagebox.showerror("Error", "Invalid deck file format!")
                return
            
            deck_name = import_data["deck_name"]
            original_name = deck_name
            counter = 1
            
            # Handle duplicate names
            while deck_name in self.data["decks"]:
                deck_name = f"{original_name} ({counter})"
                counter += 1
            
            self.data["decks"][deck_name] = import_data["deck_data"]
            self.save_data()
            
            card_count = len(import_data["deck_data"]["cards"])
            messagebox.showinfo("Success", f"Imported deck '{deck_name}' with {card_count} cards!")
            self.refresh_deck_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import deck: {e}")
    
    def show_deck_management(self, deck_name: str) -> None:
        """Show deck management interface for a specific deck."""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        cards = self.get_deck_cards(deck_name)
        
        # Title
        title_label = tk.Label(
            self.root, 
            text=f"📖 Deck: {deck_name}", 
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=20)
        
        # Stats
        stats_text = f"Cards in this deck: {len(cards)}"
        stats_label = tk.Label(
            self.root, 
            text=stats_text, 
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        stats_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        # Action buttons
        buttons = [
            ("Add New Card", lambda: self.add_card_to_deck_screen(deck_name), '#4CAF50'),
            ("Study This Deck", lambda: self.study_deck_directly(deck_name), '#FF9800'),
            ("Edit Cards", lambda: self.edit_deck_cards(deck_name), '#2196F3'),
            ("View All Cards", lambda: self.view_deck_cards(deck_name), '#9C27B0'),
            ("Back to Main Menu", self.create_main_menu, '#424242')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                width=20,
                height=2,
                font=("Arial", 11),
                bg=color,
                fg='white',
                relief='raised',
                bd=2
            )
            btn.pack(pady=8)
    
    def add_card_to_deck_screen(self, deck_name: str) -> None:
        """Show interface to add a card to a specific deck."""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text=f"Add Card to '{deck_name}'", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Question input
        tk.Label(self.root, text="Question:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=5)
        question_text = tk.Text(self.root, height=5, width=70, font=("Arial", 11))
        question_text.pack(pady=5)
        
        # Answer input
        tk.Label(self.root, text="Answer:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=5)
        answer_text = tk.Text(self.root, height=5, width=70, font=("Arial", 11))
        answer_text.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        def save_card():
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            
            if not question or not answer:
                messagebox.showwarning("Warning", "Both question and answer are required!")
                return
            
            if self.add_card_to_deck(deck_name, question, answer):
                question_text.delete("1.0", tk.END)
                answer_text.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", "Failed to add card!")
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Card",
            command=save_card,
            width=15,
            font=("Arial", 11),
            bg='#4CAF50',
            fg='white'
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Back button
        back_btn = tk.Button(
            button_frame,
            text="Back to Deck",
            command=lambda: self.show_deck_management(deck_name),
            width=15,
            font=("Arial", 11),
            bg='#2196F3',
            fg='white'
        )
        back_btn.pack(side=tk.LEFT, padx=10)
    
    def study_deck_directly(self, deck_name: str) -> None:
        """Start studying a specific deck directly."""
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("Empty Deck", f"Deck '{deck_name}' has no cards to study!")
            return
        
        self.current_deck = deck_name
        self.study_mode_selection()
    
    def study_mode_selection(self) -> None:
        """Show study mode selection screen."""
        if not self.current_deck:
            messagebox.showerror("Error", "No deck selected!")
            return
        
        cards = self.get_deck_cards(self.current_deck)
        if not cards:
            messagebox.showinfo("No Cards", f"Deck '{self.current_deck}' has no cards!")
            return
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text=f"Study Mode: {self.current_deck}", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=30)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root, 
            text=f"Choose how to study {len(cards)} cards", 
            font=("Arial", 14),
            bg='#f0f0f0',
            fg='#666'
        )
        subtitle_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=50)
        
        def start_sequential():
            self.study_mode = "sequential"
            self.prepare_study_cards()
            self.start_study_session()
        
        def start_random():
            self.study_mode = "random"
            self.prepare_study_cards()
            random.shuffle(self.study_cards)
            self.start_study_session()
        
        # Mode buttons
        sequential_btn = tk.Button(
            button_frame,
            text="Sequential Order\n(Cards in order)",
            command=start_sequential,
            width=20,
            height=3,
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white'
        )
        sequential_btn.pack(pady=15)
        
        random_btn = tk.Button(
            button_frame,
            text="Random Order\n(Shuffled cards)",
            command=start_random,
            width=20,
            height=3,
            font=("Arial", 12),
            bg='#FF9800',
            fg='white'
        )
        random_btn.pack(pady=15)
        
        # Back button
        back_btn = tk.Button(
            button_frame,
            text="Back to Deck",
            command=lambda: self.show_deck_management(self.current_deck),
            width=15,
            font=("Arial", 11),
            bg='#2196F3',
            fg='white'
        )
        back_btn.pack(pady=30)
    
    def prepare_study_cards(self) -> None:
        """Prepare the list of cards for the current study session."""
        original_cards = self.get_deck_cards(self.current_deck)
        # Create study session with card indices and original card data
        self.study_cards = []
        for i, card in enumerate(original_cards):
            self.study_cards.append({
                "original_index": i,
                "card_data": card,
                "card_id": f"{self.current_deck}_{i}"  # Unique identifier for tracking
            })
        self.known_cards = set()
    
    def start_study_session(self) -> None:
        """Start a study session."""
        self.current_card_index = 0
        self.show_answer = False
        
        # Update last studied time
        if self.current_deck in self.data["decks"]:
            self.data["decks"][self.current_deck]["last_studied"] = datetime.now().isoformat()
            self.data["decks"][self.current_deck]["stats"]["total_studies"] += 1
            self.save_data()
        
        self.show_study_card()
    
    def show_study_card(self) -> None:
        """Display the current study card."""
        if self.current_card_index >= len(self.study_cards):
            self.study_complete()
            return
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Get current card from study session
        current_study_card = self.study_cards[self.current_card_index]
        current_card = current_study_card["card_data"]
        
        # Header info
        header_frame = tk.Frame(self.root, bg='#f0f0f0')
        header_frame.pack(pady=10, fill='x')
        
        deck_label = tk.Label(
            header_frame,
            text=f"📖 {self.current_deck}",
            font=("Arial", 14, "bold"),
            bg='#f0f0f0',
            fg='#4CAF50'
        )
        deck_label.pack()
        
        progress_text = f"Card {self.current_card_index + 1} of {len(self.study_cards)} ({self.study_mode} mode)"
        progress_label = tk.Label(
            header_frame, 
            text=progress_text, 
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        progress_label.pack()
        
        # Card content frame
        card_frame = tk.Frame(self.root, bg='white', relief='raised', bd=3)
        card_frame.pack(pady=20, padx=30, fill='both', expand=True)
        
        # Question (always shown)
        question_label = tk.Label(
            card_frame,
            text="Question:",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#333'
        )
        question_label.pack(pady=15)
        
        question_text = tk.Text(
            card_frame,
            height=6,
            width=70,
            font=("Arial", 12),
            wrap=tk.WORD,
            state='disabled',
            bg='#f8f8f8'
        )
        question_text.pack(pady=5)
        question_text.config(state='normal')
        question_text.insert("1.0", current_card["question"])
        question_text.config(state='disabled')
        
        # Answer (shown/hidden based on state)
        if self.show_answer:
            answer_label = tk.Label(
                card_frame,
                text="Answer:",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='#333'
            )
            answer_label.pack(pady=(20, 5))
            
            answer_text = tk.Text(
                card_frame,
                height=6,
                width=70,
                font=("Arial", 12),
                wrap=tk.WORD,
                state='disabled',
                bg='#e8f5e8'
            )
            answer_text.pack(pady=5)
            answer_text.config(state='normal')
            answer_text.insert("1.0", current_card["answer"])
            answer_text.config(state='disabled')
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        def toggle_answer():
            self.show_answer = not self.show_answer
            self.show_study_card()
        
        def next_card():
            self.current_card_index += 1
            self.show_answer = False
            self.show_study_card()
        
        def prev_card():
            if self.current_card_index > 0:
                self.current_card_index -= 1
                self.show_answer = False
                self.show_study_card()
        
        def mark_as_known():
            """Mark card as known and remove from session."""
            current_study_card = self.study_cards[self.current_card_index]
            card_id = current_study_card["card_id"]
            self.known_cards.add(card_id)
            
            # Remove this card from the study session
            self.study_cards.pop(self.current_card_index)
            
            # Adjust current index if needed
            if self.current_card_index >= len(self.study_cards):
                if len(self.study_cards) > 0:
                    self.current_card_index = 0
            
            self.show_answer = False
            self.show_study_card()
        
        def need_more_study():
            """Duplicate this card 2 more times in the session."""
            current_study_card = self.study_cards[self.current_card_index]
            
            # Add 2 more copies of this card to the end of the study session
            for _ in range(2):
                duplicate_card = {
                    "original_index": current_study_card["original_index"],
                    "card_data": current_study_card["card_data"],
                    "card_id": current_study_card["card_id"] + f"_dup_{len(self.study_cards)}"
                }
                self.study_cards.append(duplicate_card)
            
            # Move to next card
            next_card()
        
        # Control buttons - First row
        if not self.show_answer:
            show_answer_btn = tk.Button(
                button_frame,
                text="Show Answer",
                command=toggle_answer,
                width=15,
                font=("Arial", 11),
                bg='#4CAF50',
                fg='white'
            )
            show_answer_btn.pack(side=tk.LEFT, padx=5)
        else:
            hide_answer_btn = tk.Button(
                button_frame,
                text="Hide Answer",
                command=toggle_answer,
                width=15,
                font=("Arial", 11),
                bg='#FF9800',
                fg='white'
            )
            hide_answer_btn.pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        if self.current_card_index > 0:
            prev_btn = tk.Button(
                button_frame,
                text="Previous",
                command=prev_card,
                width=15,
                font=("Arial", 11),
                bg='#2196F3',
                fg='white'
            )
            prev_btn.pack(side=tk.LEFT, padx=5)
        
        if self.current_card_index < len(self.study_cards) - 1:
            next_btn = tk.Button(
                button_frame,
                text="Next",
                command=next_card,
                width=15,
                font=("Arial", 11),
                bg='#2196F3',
                fg='white'
            )
            next_btn.pack(side=tk.LEFT, padx=5)
        
        # End session button
        end_btn = tk.Button(
            button_frame,
            text="End Session",
            command=lambda: self.show_deck_management(self.current_deck),
            width=15,
            font=("Arial", 11),
            bg='#f44336',
            fg='white'
        )
        end_btn.pack(side=tk.LEFT, padx=5)
        
        # Second row of buttons - Study feedback (only show if answer is visible)
        if self.show_answer and len(self.study_cards) > 0:
            button_frame2 = tk.Frame(self.root, bg='#f0f0f0')
            button_frame2.pack(pady=10)
            
            know_btn = tk.Button(
                button_frame2,
                text="✓ I Know This",
                command=mark_as_known,
                width=18,
                font=("Arial", 11, "bold"),
                bg='#4CAF50',
                fg='white'
            )
            know_btn.pack(side=tk.LEFT, padx=10)
            
            study_more_btn = tk.Button(
                button_frame2,
                text="📚 Need More Study",
                command=need_more_study,
                width=18,
                font=("Arial", 11, "bold"),
                bg='#FF5722',
                fg='white'
            )
            study_more_btn.pack(side=tk.LEFT, padx=10)
    
    def study_complete(self) -> None:
        """Show study complete screen."""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        original_cards = self.get_deck_cards(self.current_deck)
        cards_known = len(self.known_cards)
        
        # Completion message
        tk.Label(
            self.root,
            text="🎉 Study Session Complete!",
            font=("Arial", 22, "bold"),
            bg='#f0f0f0',
            fg='#4CAF50'
        ).pack(pady=40)
        
        tk.Label(
            self.root,
            text=f"Deck: {self.current_deck}",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#333'
        ).pack(pady=10)
        
        # Session stats
        stats_text = f"Original cards: {len(original_cards)} | Cards mastered: {cards_known}"
        if cards_known > 0:
            stats_text += f" | Mastery rate: {cards_known/len(original_cards)*100:.1f}%"
        
        tk.Label(
            self.root,
            text=stats_text,
            font=("Arial", 14),
            bg='#f0f0f0'
        ).pack(pady=20)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=40)
        
        # Action buttons
        study_again_btn = tk.Button(
            button_frame,
            text="Study Again",
            command=self.study_mode_selection,
            width=18,
            height=2,
            font=("Arial", 11),
            bg='#4CAF50',
            fg='white'
        )
        study_again_btn.pack(side=tk.LEFT, padx=10)
        
        deck_menu_btn = tk.Button(
            button_frame,
            text="Back to Deck",
            command=lambda: self.show_deck_management(self.current_deck),
            width=18,
            height=2,
            font=("Arial", 11),
            bg='#2196F3',
            fg='white'
        )
        deck_menu_btn.pack(side=tk.LEFT, padx=10)
        
        main_menu_btn = tk.Button(
            button_frame,
            text="Main Menu",
            command=self.create_main_menu,
            width=18,
            height=2,
            font=("Arial", 11),
            bg='#424242',
            fg='white'
        )
        main_menu_btn.pack(side=tk.LEFT, padx=10)
    
    def edit_deck_cards(self, deck_name: str) -> None:
        """Show the edit cards interface for a specific deck."""
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("No Cards", f"Deck '{deck_name}' has no cards to edit!")
            return
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text=f"Edit Cards in '{deck_name}'", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Create a frame with scrollbar for the card list
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Scrollbar and listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        card_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=15
        )
        card_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=card_listbox.yview)
        
        # Populate listbox with cards
        for i, card in enumerate(cards):
            preview = card["question"][:80] + "..." if len(card["question"]) > 80 else card["question"]
            card_listbox.insert(tk.END, f"{i+1}. {preview}")
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        def edit_selected():
            selection = card_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a card to edit!")
                return
            
            card_idx = selection[0]
            self.edit_single_deck_card(deck_name, card_idx)
        
        def delete_selected():
            selection = card_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a card to delete!")
                return
            
            card_idx = selection[0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this card?"):
                self.data["decks"][deck_name]["cards"].pop(card_idx)
                self.save_data()
                self.edit_deck_cards(deck_name)  # Refresh the screen
        
        # Buttons
        edit_btn = tk.Button(
            button_frame,
            text="Edit Selected",
            command=edit_selected,
            width=15,
            font=("Arial", 11),
            bg='#FF9800',
            fg='white'
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            button_frame,
            text="Delete Selected",
            command=delete_selected,
            width=15,
            font=("Arial", 11),
            bg='#f44336',
            fg='white'
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(
            button_frame,
            text="Back to Deck",
            command=lambda: self.show_deck_management(deck_name),
            width=15,
            font=("Arial", 11),
            bg='#2196F3',
            fg='white'
        )
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def edit_single_deck_card(self, deck_name: str, card_index: int) -> None:
        """Edit a single card in a deck."""
        cards = self.get_deck_cards(deck_name)
        if card_index >= len(cards):
            messagebox.showerror("Error", "Card not found!")
            return
        
        card = cards[card_index]
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text=f"Edit Card #{card_index + 1} in '{deck_name}'", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Question input
        tk.Label(self.root, text="Question:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=5)
        question_text = tk.Text(self.root, height=5, width=70, font=("Arial", 11))
        question_text.pack(pady=5)
        question_text.insert("1.0", card["question"])
        
        # Answer input
        tk.Label(self.root, text="Answer:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=5)
        answer_text = tk.Text(self.root, height=5, width=70, font=("Arial", 11))
        answer_text.pack(pady=5)
        answer_text.insert("1.0", card["answer"])
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        def save_changes():
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            
            if not question or not answer:
                messagebox.showwarning("Warning", "Both question and answer are required!")
                return
            
            # Update the card
            self.data["decks"][deck_name]["cards"][card_index]["question"] = question
            self.data["decks"][deck_name]["cards"][card_index]["answer"] = answer
            self.save_data()
            
            messagebox.showinfo("Success", "Card updated successfully!")
            self.edit_deck_cards(deck_name)
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes,
            width=15,
            font=("Arial", 11),
            bg='#4CAF50',
            fg='white'
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=lambda: self.edit_deck_cards(deck_name),
            width=15,
            font=("Arial", 11),
            bg='#f44336',
            fg='white'
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def view_deck_cards(self, deck_name: str) -> None:
        """Show all cards in a deck in a read-only view."""
        cards = self.get_deck_cards(deck_name)
        if not cards:
            messagebox.showinfo("No Cards", f"Deck '{deck_name}' has no cards to display!")
            return
        
        # Create a new window for viewing cards
        view_window = tk.Toplevel(self.root)
        view_window.title(f"All Cards in '{deck_name}'")
        view_window.geometry("900x700")
        view_window.configure(bg='#f0f0f0')
        
        # Title
        title_label = tk.Label(
            view_window, 
            text=f"📖 {deck_name} - All Cards ({len(cards)} total)", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(view_window, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display each card
        for i, card in enumerate(cards):
            card_frame = tk.Frame(scrollable_frame, bg='white', relief='raised', bd=1)
            card_frame.pack(pady=10, padx=20, fill='x')
            
            # Card number
            number_label = tk.Label(
                card_frame,
                text=f"Card #{i+1}",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='#4CAF50'
            )
            number_label.pack(pady=5)
            
            # Question
            tk.Label(card_frame, text="Q:", font=("Arial", 10, "bold"), bg='white').pack(anchor='w', padx=10)
            question_label = tk.Label(
                card_frame,
                text=card["question"],
                font=("Arial", 10),
                bg='white',
                wraplength=800,
                justify='left'
            )
            question_label.pack(anchor='w', padx=20, pady=2)
            
            # Answer
            tk.Label(card_frame, text="A:", font=("Arial", 10, "bold"), bg='white').pack(anchor='w', padx=10)
            answer_label = tk.Label(
                card_frame,
                text=card["answer"],
                font=("Arial", 10),
                bg='white',
                wraplength=800,
                justify='left'
            )
            answer_label.pack(anchor='w', padx=20, pady=2)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = tk.Button(
            view_window,
            text="Close",
            command=view_window.destroy,
            width=15,
            font=("Arial", 11),
            bg='#2196F3',
            fg='white'
        )
        close_btn.pack(pady=10)
    
    def run(self) -> None:
        """Start the application."""
        print("Starting Offline Flashcard App with Deck Organization...")
        print(f"Data file: {self.DATA_FILE}")
        
        deck_count = len(self.data["decks"])
        total_cards = sum(len(deck["cards"]) for deck in self.data["decks"].values())
        print(f"Loaded {deck_count} decks with {total_cards} total cards")
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.save_data()  # Save before closing
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        self.root.mainloop()

def main():
    """Main function to run the application."""
    app = FlashcardApp()
    app.run()

if __name__ == "__main__":
    main()