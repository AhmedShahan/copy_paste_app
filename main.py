import tkinter as tk
from tkinter import ttk
import pyperclip
import time
import keyboard

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.root.geometry("500x400")
        self.root.attributes("-topmost", True)  # Keep on top of other windows
        
        self.clipboard_history = []
        self.selected_index = None
        self.stop_monitoring = False
        self.last_clipboard_content = ""
        
        # Create the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Clipboard History", font=("Helvetica", 14))
        title_label.pack(pady=(0, 10))
        
        # Create frame for the listbox and scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox for history items
        self.history_listbox = tk.Listbox(
            list_frame, 
            height=10, 
            width=50, 
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 10),
            selectbackground="#a6a6a6",
            selectmode=tk.SINGLE
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Bind selection event
        self.history_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        paste_button = ttk.Button(button_frame, text="Paste", command=self.paste_item)
        paste_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Helvetica", 9))
        self.status_label.pack(pady=5)
        
        # Initialize last clipboard content
        try:
            self.last_clipboard_content = pyperclip.paste()
        except:
            self.last_clipboard_content = ""
        
        # Start clipboard monitoring
        self.check_clipboard()
    
    def check_clipboard(self):
        """Check clipboard content periodically"""
        if not self.stop_monitoring:
            try:
                current_content = pyperclip.paste()
                
                # If content has changed
                if current_content != self.last_clipboard_content and current_content.strip():
                    # Check if the content is not already in the history
                    if current_content not in self.clipboard_history:
                        self.clipboard_history.insert(0, current_content)
                        self.update_listbox()
                        self.status_label.config(
                            text=f"Added: {current_content[:30]}{'...' if len(current_content) > 30 else ''}"
                        )
                    
                    self.last_clipboard_content = current_content
            except Exception as e:
                self.status_label.config(text=f"Clipboard error: {str(e)}")
            
            # Schedule the next check after 100ms
            self.root.after(100, self.check_clipboard)
    
    def update_listbox(self):
        """Update the listbox with current history items"""
        self.history_listbox.delete(0, tk.END)
        for item in self.clipboard_history:
            # Truncate long items for display
            display_text = item if len(item) <= 50 else item[:47] + "..."
            self.history_listbox.insert(tk.END, display_text)
    
    def on_select(self, event):
        """Handle listbox selection"""
        if self.history_listbox.curselection():
            self.selected_index = self.history_listbox.curselection()[0]
    
    def paste_item(self):
        """Paste the selected item or the top item if none selected"""
        if not self.clipboard_history:
            self.status_label.config(text="No items to paste")
            return
        
        # If nothing is selected, paste the top item
        if self.selected_index is None:
            self.selected_index = 0
        
        # Get the item to paste
        item_to_paste = self.clipboard_history[self.selected_index]
        
        # Copy it to clipboard
        pyperclip.copy(item_to_paste)
        
        # Highlight the item in the listbox
        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(self.selected_index)
        self.history_listbox.see(self.selected_index)
        
        # Minimize window briefly to allow focus to return to the previous application
        self.root.iconify()
        self.root.after(100, self.perform_paste)
        
        # Update status
        self.status_label.config(text=f"Pasted item {self.selected_index + 1}")
        
        # Move to the next item for next paste
        if self.selected_index < len(self.clipboard_history) - 1:
            self.selected_index += 1
        else:
            self.selected_index = 0
    
    def perform_paste(self):
        """Simulate Ctrl+V keyboard press to paste content"""
        try:
            # Restore window
            self.root.deiconify()
            
            # Simulate keyboard paste (Ctrl+V)
            keyboard.press_and_release('ctrl+v')
        except Exception as e:
            self.status_label.config(text=f"Paste error: {str(e)}")
    
    def clear_history(self):
        """Clear all history items"""
        self.clipboard_history = []
        self.selected_index = None
        self.history_listbox.delete(0, tk.END)
        self.status_label.config(text="History cleared")
    
    def exit_app(self):
        """Exit the application"""
        self.stop_monitoring = True
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()