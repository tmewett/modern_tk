# modern_tk

Quality: WIP/experimental

Tcl/Tk is quite a useful piece of kit: a powerful, cross-platform GUI system with a simple scripting language interface.

However, since no one uses Tcl, all that power is behind language-specific bindings like Python's Tkinter. The documentation for bindings is rarely complete, and it's a hurdle for new users to have to translate concepts from the main Tk documentation; so they are hard to learn and fragment Tk knowledge across different languages.

*modern_tk* is an experiment to expose Tcl more directly in a language, namely Python. It:

- allows you to easily evaluate Tcl code, embedding Python values and callbacks
- is fully **asynchronous** using asyncio (instead of having its own blocking loop like Tkinter)
- is **pure Python**, using inter-process communication instead of C linking
- is easy to port to other languages with minimal API changes.

## Example

```python
import asyncio
import modern_tk

async def main():
    async with modern_tk.AsyncioTk("tclsh") as tk:
        clicks = 0
        async def on_click():
            nonlocal clicks
            clicks += 1
            await tk(".b configure -text ?", f"Clicks: {clicks}")
        await tk("""
            ttk::button .b -text "Clicks: 0" -command ?
            grid .b -padx 50 -pady 50
        """, on_click)
        await tk.wait()

asyncio.run(main())
```

Equivalent with Tkinter:

```python
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
```
