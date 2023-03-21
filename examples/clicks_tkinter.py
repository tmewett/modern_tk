import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()

clicks = 0
def on_click():
    global clicks
    clicks += 1
    b['text'] = f"Clicks: {clicks}"

b = ttk.Button(root, text="Clicks: 0", command=on_click)
b.grid(padx=50, pady=50)

root.mainloop()
