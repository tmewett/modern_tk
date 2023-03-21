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
