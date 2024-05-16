import tkinter as tk
from tkinter import messagebox

def on_exit():
    """Handle exit menu item."""
    if messagebox.askokcancel("Exit", "Do you really want to quit?"):
        root.destroy()

def show_message():
    """Display a dummy message."""
    messagebox.showinfo("Information", "This is a sample GUI.")

# Create the main window
root = tk.Tk()
# Set the default size of the window
root.geometry("1024x768")
root.title("Enhanced Sample GUI")

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add a file menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=on_exit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add a toolbar
toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
toolbar.pack(side=tk.TOP, fill=tk.X)

btn_exit = tk.Button(toolbar, text="Exit", command=on_exit)
btn_exit.pack(side=tk.LEFT, padx=2, pady=2)

btn_info = tk.Button(toolbar, text="Info", command=show_message)
btn_info.pack(side=tk.LEFT, padx=2, pady=2)

# Add a status bar
status = tk.Label(root, text="Ready...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status.pack(side=tk.BOTTOM, fill=tk.X)

# Create a Label in the main window
welcome_label = tk.Label(root, text="Welcome to the Enhanced Sample GUI!", padx=10, pady=10)
welcome_label.pack()

# Start the event loop
root.mainloop()
