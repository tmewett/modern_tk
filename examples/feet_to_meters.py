import asyncio

import modern_tk


async def main():
    async with modern_tk.AsyncioTk("tclsh") as tk:
        await tk("""
            wm title . "Feet to Meters"
            grid [ttk::frame .c -padding "3 3 12 12"] -column 0 -row 0 -sticky nwes
            grid columnconfigure . 0 -weight 1; grid rowconfigure . 0 -weight 1

            grid [ttk::entry .c.feet -width 7] -column 2 -row 1 -sticky we
            grid [ttk::label .c.meters] -column 2 -row 2 -sticky we
            grid [ttk::button .c.calc -text "Calculate"] -column 3 -row 3 -sticky w

            grid [ttk::label .c.flbl -text "feet"] -column 3 -row 1 -sticky w
            grid [ttk::label .c.islbl -text "is equivalent to"] -column 1 -row 2 -sticky e
            grid [ttk::label .c.mlbl -text "meters"] -column 3 -row 2 -sticky w

            foreach w [winfo children .c] {grid configure $w -padx 5 -pady 5}
            focus .c.feet
        """)
        async def calculate():
            feet = await tk(".c.feet get")
            await tk(".c.meters configure -text ?", float(feet) * 0.3048)
        await tk("bind . <Return> ?", calculate)
        await tk(".c.calc configure -command ?", calculate)
        await tk.wait()

asyncio.run(main())
