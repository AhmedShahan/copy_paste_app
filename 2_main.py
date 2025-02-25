import tkinter as tk
from tkinter import ttk
import pyperclip
import time
from pynput.keyboard import Controller, Key
import time
class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.root.geometry("500x400")
        self.root.attributes("-topmost", True)  # Keep on top of other windows
        
        self.clipboard_history = []
        self.paste_index = 0  # Index for sequential pasting
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
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        self.paste_button = ttk.Button(button_frame, text="Paste Next Item", command=self.paste_next_item)
        self.paste_button.pack(side=tk.LEFT, padx=5)
        
        reset_button = ttk.Button(button_frame, text="Reset Paste Order", command=self.reset_paste_order)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # Currently selected item label
        self.current_item_label = ttk.Label(main_frame, text="Next item to paste: None", font=("Helvetica", 9))
        self.current_item_label.pack(pady=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Helvetica", 9))
        self.status_label.pack(pady=5)
        
        # Initialize last clipboard content
        try:
            self.last_clipboard_content = pyperclip.paste()
        except:
            self.last_clipboard_content = ""
            self.status_label.config(text="Warning: Could not access clipboard")
        
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
                        # Update paste button state
                        self.paste_button.config(state=tk.NORMAL)
                        # Update currently selected item text
                        self.update_current_item_text()
                    
                    self.last_clipboard_content = current_content
            except Exception as e:
                self.status_label.config(text=f"Clipboard error: {str(e)}")
            
            # Schedule the next check after 100ms
            self.root.after(100, self.check_clipboard)
    
    def update_listbox(self):
        """Update the listbox with current history items"""
        self.history_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.clipboard_history):
            # Truncate long items for display
            display_text = item if len(item) <= 50 else item[:47] + "..."
            
            # Mark the current paste index
            if idx == self.paste_index:
                display_text = "► " + display_text
            
            self.history_listbox.insert(tk.END, display_text)
        
        # Highlight the current paste index
        if self.clipboard_history:
            self.history_listbox.selection_clear(0, tk.END)
            self.history_listbox.selection_set(self.paste_index)
            self.history_listbox.see(self.paste_index)
    
    def update_current_item_text(self):
        """Update the text showing the next item to be pasted"""
        if not self.clipboard_history:
            self.current_item_label.config(text="Next item to paste: None")
            self.paste_button.config(state=tk.DISABLED)
        else:
            item = self.clipboard_history[self.paste_index]
            display_text = item if len(item) <= 30 else item[:27] + "..."
            self.current_item_label.config(text=f"Next item to paste: {display_text}")
            self.paste_button.config(state=tk.NORMAL)
    # Add this to your imports


# Then modify your paste_next_item method
    def paste_next_item(self):
        """Copy the next sequential item to clipboard and simulate paste keystroke"""
        if not self.clipboard_history:
            self.status_label.config(text="No items to paste")
            return
        
        # Get the next item to paste
        item_to_paste = self.clipboard_history[self.paste_index]
        
        # Copy it to clipboard
        pyperclip.copy(item_to_paste)
        
        # Update status
        self.status_label.config(text=f"Pasting: {item_to_paste[:30]}...")
        
        # Give time for the clipboard to update
        time.sleep(0.1)
        
        # Create keyboard controller
        keyboard = Controller()
        
        # Minimize the clipboard manager window to focus on the background window
        self.root.iconify()
        
        # Give time for window focus to change
        time.sleep(0.5)
        
        # Simulate Ctrl+V (or Command+V on Mac)
        with keyboard.pressed(Key.ctrl):  # Use Key.cmd on Mac
            keyboard.press('v')
            keyboard.release('v')
        
        # Move to the next item for next paste
        self.paste_index = (self.paste_index + 1) % len(self.clipboard_history)
        
        # Update the highlighted item and text
        self.update_listbox()
        self.update_current_item_text()
    
    def reset_paste_order(self):
        """Reset the paste index to start from the beginning"""
        self.paste_index = 0
        self.update_listbox()
        self.update_current_item_text()
        self.status_label.config(text="Paste order reset to beginning")
    
    def clear_history(self):
        """Clear all history items"""
        self.clipboard_history = []
        self.paste_index = 0
        self.history_listbox.delete(0, tk.END)
        self.update_current_item_text()
        self.status_label.config(text="History cleared")
    
    def exit_app(self):
        """Exit the application"""
        self.stop_monitoring = True
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()