import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import threading
import pyautogui
import keyboard
import time
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


class ColorClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trigger")
        self.root.geometry("400x300")
        self.selected_color = None
        self.toggle_key = None
        self.tray_icon = None

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=6)
        self.style.configure("TLabel", font=("Arial", 12))

        self.color_button = ttk.Button(root, text="Rang tanlash", command=self.pick_color)
        self.color_button.pack(pady=10)

        self.pick_color_button = ttk.Button(root, text="Kistichka bilan rang tanlash", command=self.pick_color_from_screen)
        self.pick_color_button.pack(pady=10)

        self.color_label = ttk.Label(root, text="Tanlangan rang: Yo'q", background="white", width=30)
        self.color_label.pack(pady=10)

        self.hotkeys_button = ttk.Button(root, text="Hot Keys", command=self.set_hotkey)
        self.hotkeys_button.pack(pady=10)

        self.minimize_button = ttk.Button(root, text="Свернуть", command=self.minimize_to_tray)
        self.minimize_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def pick_color(self):
        color_code = colorchooser.askcolor(title="Rang tanlang")[1]
        if color_code:
            self.selected_color = color_code
            self.color_label.config(text=f"Tanlangan rang: {self.selected_color}", background=self.selected_color)

    def pick_color_from_screen(self):
        messagebox.showinfo("Kistichka", "Iltimos, ekranda tanlamoqchi bo'lgan rang ustiga kursorni olib boring va [Ctrl] tugmasini bosing.")
        while True:
            if keyboard.is_pressed("ctrl"):
                x, y = pyautogui.position()
                self.selected_color = self.rgb_to_hex(pyautogui.screenshot().getpixel((x, y)))
                self.color_label.config(text=f"Tanlangan rang: {self.selected_color}", background=self.selected_color)
                break

    def set_hotkey(self):
        messagebox.showinfo("Hot Keys", "Iltimos, hotkey tanlash uchun klavishani bosib turing.")
        self.toggle_key = keyboard.read_event().name
        messagebox.showinfo("Tanlangan", f"Hotkey: {self.toggle_key}")
        threading.Thread(target=self.listen_for_hotkey, daemon=True).start()

    def listen_for_hotkey(self):
        while True:
            if self.toggle_key and keyboard.is_pressed(self.toggle_key):
                self.run_clicker()
            time.sleep(0.1)

    def run_clicker(self):
        while keyboard.is_pressed(self.toggle_key):
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size

            for x in range(0, width, 10):
                for y in range(0, height, 10):
                    if not keyboard.is_pressed(self.toggle_key):  # Tugma qo‘yib yuborilganida chiqadi
                        return
                    color = screenshot.getpixel((x, y))
                    if self.rgb_to_hex(color) == self.selected_color:
                        pyautogui.click(x, y)

    def minimize_to_tray(self):
        self.root.withdraw()
        image = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill="blue")
        draw.text((16, 16), "CC", fill="white")

        menu = Menu(MenuItem("Ochish", self.show_window), MenuItem("Chiqish", self.exit_app))
        self.tray_icon = Icon("Trigger", image, "Trigger", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.root.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()

    def exit_app(self):
        self.root.quit()
        if self.tray_icon:
            self.tray_icon.stop()

    @staticmethod
    def rgb_to_hex(rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


root = tk.Tk()
app = ColorClickerApp(root)
root.mainloop()
