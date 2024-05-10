import sys
import customtkinter as ctk
from win32api import GetSystemMetrics
from config import Config
import config
config = Config()

DISPLAY_SIZE = [GetSystemMetrics(0), GetSystemMetrics(1)]
DEV_WINDOW_WIDTH = config.retrieveConfig('DEV_WINDOW_WIDTH')
WIN_SIZE_Y = config.retrieveConfig('WIN_SIZE_Y')

WIN_SIZE_X = DEV_WINDOW_WIDTH
WIN_SIZE_Y = DISPLAY_SIZE[1]


class DevUI:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Dev Window")
        self.app.overrideredirect(True)
        self.app.geometry(f"{WIN_SIZE_X}x{WIN_SIZE_Y}+0+0")
        self.is_running = True
        self.dev_ui_wants_update = True
        self.objects = None
        self.valid_objects = False
        self.button = ctk.CTkButton(self.app, text="Click Me", command=self.on_button_click)
        self.button.pack()

        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def update(self):
        self.app.update_idletasks()
        self.app.update()
        if self.valid_objects: ...

    def on_button_click(self):
        print("Button clicked!")

    def destroy(self):
        print('destroying')
        self.app.quit()
        self.app.destroy()
        sys.exit()