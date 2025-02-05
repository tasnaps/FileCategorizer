# main.py
from ui import OrganizerApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = OrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
