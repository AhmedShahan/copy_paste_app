import tkinter as tk
from tkinter import ttk
import subprocess
import pyperclip
import time
from pynput.keyboard import Controller, Key

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.root.geometry("500x400")
        
        self.clipboard_history = []
        self.dragged_item = None
        self.last_clipboard_content = ""
        
        # Main UI setup
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with drag support
        self.listbox = tk.Listbox(
            main_frame,
            height=15,
            width=60,
            selectmode=tk.SINGLE,
            font=("DejaVu Sans", 10),
            exportselection=False
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # Bind drag events
        self.listbox.bind("<ButtonPress-1>", self.start_drag)
        self.listbox.bind("<B1-Motion>", self.on_drag)
        self.listbox.bind("<ButtonRelease-1>", self.end_drag)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        reset_button = ttk.Button(button_frame, text="Reset", command=self.full_reset)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack()
        
        # Clipboard monitoring
        self.check_clipboard()

    def start_drag(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.dragged_item = self.clipboard_history[selection[0]]
            self.copy_to_selections(self.dragged_item)
            self.status_label.config(text=f"Dragging: {self.dragged_item[:30]}...")

    def copy_to_selections(self, text):
        """Copy text to both clipboard and primary selection"""
        try:
            # Copy to CLIPBOARD (Ctrl+V)
            pyperclip.copy(text)
            
            # Copy to PRIMARY (middle-click)
            process = subprocess.Popen(
                ['xclip', '-selection', 'primary'],
                stdin=subprocess.PIPE,
                close_fds=True
            )
            process.communicate(input=text.encode('utf-8'))
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def on_drag(self, event):
        """Update drag visual feedback"""
        if self.dragged_item:
            self.listbox.config(selectbackground="#4a90d9")

    def end_drag(self, event):
        if self.dragged_item:
            try:
                # Simulate middle-click paste
                keyboard = Controller()
                
                # Release window focus
                self.root.wm_attributes("-topmost", False)
                time.sleep(0.2)
                
                # Send middle-click (requires xdotool)
                subprocess.run(["xdotool", "click", "1"])
                
                self.status_label.config(text="Pasted to target application!")
                self.listbox.config(selectbackground="#a6a6a6")
                self.dragged_item = None
                self.root.wm_attributes("-topmost", True)
                
            except Exception as e:
                self.status_label.config(text=f"Paste error: {str(e)}")
                self.root.wm_attributes("-topmost", True)

    def check_clipboard(self):
        try:
            current_content = pyperclip.paste()
            if current_content != self.last_clipboard_content and current_content.strip():
                if current_content not in self.clipboard_history:
                    self.clipboard_history.insert(0, current_content)
                    self.update_listbox()
                self.last_clipboard_content = current_content
        except Exception as e:
            pass
        self.root.after(100, self.check_clipboard)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.clipboard_history:
            display_text = item[:80] + ("..." if len(item) > 80 else "")
            self.listbox.insert(tk.END, display_text)

    def full_reset(self):
        """Reset both history and current clipboard"""
        self.clipboard_history = []
        pyperclip.copy('')  # Clear current clipboard
        self.last_clipboard_content = ""
        self.update_listbox()
        self.status_label.config(text="Full reset complete: History and clipboard cleared")

    def clear_history(self):
        """Clear just the history"""
        self.clipboard_history = []
        self.update_listbox()
        self.status_label.config(text="History cleared")

    def exit_app(self):
        """Close the application"""
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()