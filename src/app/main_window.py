import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import random
import os
import subprocess
import sys

from src.utils import resource_path
from src.ui.settings_window import SettingsWindow
from src.ui.theme import theme

class Bubble:
    def __init__(self, canvas, width, height):
        self.canvas, self.width, self.height = canvas, width, height
        self.radius = random.randint(20, 50)
        self.x, self.y = random.randint(self.radius, width - self.radius), random.randint(self.radius, height - self.radius)
        self.dx, self.dy = random.choice([-1.5, -1, 1, 1.5]), random.choice([-1.5, -1, 1, 1.5])
        # Using a list of related colors from the theme for the bubbles
        bubble_colors = [theme["primary"], theme["secondary"], theme["button_primary_hover"]]
        self.color = random.choice(bubble_colors)
        self.id = self.canvas.create_oval(self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius, fill=self.color, outline="")

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if not self.radius < self.x < self.width - self.radius:
            self.dx *= -1
        if not self.radius < self.y < self.height - self.radius:
            self.dy *= -1
        self.canvas.coords(self.id, self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius)

class MainApplication(tk.Frame):
    def __init__(self, parent, capture_module, recording_module, app_config):
        super().__init__(parent)
        self.parent = parent
        self.capture_module = capture_module
        self.recording_module = recording_module
        self.app_config = app_config
        self.record_all_screens_var = tk.BooleanVar(value=False)
        self.configure(bg=theme["window_bg"])

        self.canvas = tk.Canvas(self, bg=theme["window_bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bubbles = [Bubble(self.canvas, 1280, 720) for _ in range(20)]
        self.create_widgets()
        self.animate_bubbles()
        self.parent.bind("<Configure>", self.on_window_resize)

    def animate_bubbles(self):
        for bubble in self.bubbles:
            bubble.move()
        self.after(33, self.animate_bubbles)

    def create_widgets(self):
        self.main_card_frame = tk.Frame(self.canvas, bg=theme["card_bg"], bd=1, relief="solid")
        self.main_card_id = self.canvas.create_window(0, 0, window=self.main_card_frame, anchor="center")
        header_container = tk.Frame(self.main_card_frame, bg=theme["card_bg"], padx=20, pady=15)
        header_container.pack(fill="x", expand=True, pady=(10,0))
        try:
            logo_image = Image.open(resource_path("assets/logo_guara.png"))
            logo_image.thumbnail((200, 60))
            self.logo_tk = ImageTk.PhotoImage(logo_image)
            tk.Label(header_container, image=self.logo_tk, bg=theme["card_bg"]).pack(pady=(0,10))
        except FileNotFoundError:
            pass
        tk.Label(header_container, text="Sentinela Guará", font=("Segoe UI", 26, "bold"), bg=theme["card_bg"], fg=theme["text_primary"]).pack()
        tk.Label(header_container, text="Gravador de evidências simples e seguro", font=("Segoe UI", 10), bg=theme["card_bg"], fg=theme["text_secondary"]).pack(pady=(0,10))
        tk.Frame(self.main_card_frame, height=1, bg=theme["separator"]).pack(fill="x", padx=40, pady=(15,10))
        content_container = tk.Frame(self.main_card_frame, bg=theme["card_bg"], padx=40, pady=20)
        content_container.pack(expand=True, fill="both")
        btn1 = tk.Button(content_container, text="INICIAR CAPTURA (F9)", font=("Segoe UI", 10, "bold"), bg=theme["button_primary_bg"], fg="white", relief=tk.FLAT, padx=20, pady=8, command=self.capture_module.start_capture_session)
        btn1.pack(pady=(5,10), fill='x')
        btn2 = tk.Button(content_container, text="INICIAR GRAVAÇÃO (F10)", font=("Segoe UI", 10, "bold"), bg=theme["button_primary_bg"], fg="white", relief=tk.FLAT, padx=20, pady=8, command=lambda: self.recording_module.enter_preparation_mode(record_all_screens=self.record_all_screens_var.get()))
        btn2.pack(pady=(5,10), fill='x')

        record_all_checkbox = tk.Checkbutton(
            content_container,
            text="Gravar todas as telas simultaneamente (experimental)",
            variable=self.record_all_screens_var,
            bg=theme["card_bg"],
            fg=theme["text_secondary"],
            activebackground=theme["card_bg"],
            activeforeground=theme["text_primary"],
            selectcolor=theme["window_bg"],
            font=("Segoe UI", 9)
        )
        record_all_checkbox.pack(pady=(0, 10))

        for btn in [btn1, btn2]:
            btn.bind("<Enter>", lambda e: e.widget.config(bg=theme["button_primary_hover"]))
            btn.bind("<Leave>", lambda e: e.widget.config(bg=theme["button_primary_bg"]))

        footer_frame = tk.Frame(self.main_card_frame, bg=theme["window_bg"], pady=5)
        footer_frame.pack(side="bottom", fill="x", pady=(10,0))

        btn_open_folder = tk.Button(footer_frame, text="Abrir Pasta de Evidências", font=("Segoe UI", 8, "bold"), command=self.open_evidence_folder, relief=tk.FLAT, bg=theme["button_secondary_bg"], fg="white")
        btn_open_folder.pack(side=tk.LEFT, padx=10)
        btn_open_folder.bind("<Enter>", lambda e: e.widget.config(bg=theme["button_secondary_hover"]))
        btn_open_folder.bind("<Leave>", lambda e: e.widget.config(bg=theme["button_secondary_bg"]))

        tk.Label(footer_frame, text="Código by Victor Ladislau Viana", font=("Segoe UI", 8), bg=footer_frame.cget('bg'), fg=theme["text_secondary"]).pack(side=tk.LEFT, padx=10)

        btn_settings = tk.Button(footer_frame, text="⚙", font=("Segoe UI", 12), command=self.open_settings, relief=tk.FLAT, bg=footer_frame.cget('bg'), fg=theme["text_secondary"])
        btn_settings.pack(side=tk.RIGHT, padx=10)

        self.parent.after(10, self.on_window_resize)

    def on_window_resize(self, event=None):
        w, h = self.parent.winfo_width(), self.parent.winfo_height()
        self.canvas.config(width=w, height=h)
        if hasattr(self, 'main_card_id'):
            self.canvas.coords(self.main_card_id, w/2, h/2)
        for bubble in self.bubbles:
            bubble.width, bubble.height = w, h

    def open_evidence_folder(self):
        folder_to_open = self.app_config["DefaultSaveLocation"]
        try:
            subprocess.Popen(f'explorer "{os.path.realpath(folder_to_open)}"')
        except Exception as e:
            print(f"Não foi possível abrir a pasta de evidências: {e}")

    def open_settings(self):
        SettingsWindow(self.parent, self.app_config, self.on_settings_closed)

    def on_settings_closed(self, new_save_path):
        self.app_config["DefaultSaveLocation"] = new_save_path
        self.capture_module.save_path = new_save_path
        self.recording_module.save_path = new_save_path
