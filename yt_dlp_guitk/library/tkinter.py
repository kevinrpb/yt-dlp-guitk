import tkinter as tk


def center_window(window: tk.Toplevel):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center

    See https://stackoverflow.com/a/10018670
    """
    window.attributes("-alpha", 0.0)  # First, 'hide' the window so we don't see it moving.
    window.update_idletasks()  # This ensures the hiding takes place

    width = window.winfo_width()
    height = window.winfo_height()

    frame_width = window.winfo_rootx() - window.winfo_x()
    window_width = width + 2 * frame_width
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    window_height = height + titlebar_height + frame_width

    x = window.winfo_screenwidth() // 2 - window_width // 2
    y = window.winfo_screenheight() // 2 - window_height // 2

    window.geometry(f"{width}x{height}+{x}+{y}")  # This is what sets the window in the center
    window.deiconify()  # This is to make the window get focus

    window.attributes("-alpha", 1.0)  # With this we show the window back again
    window.update_idletasks()
