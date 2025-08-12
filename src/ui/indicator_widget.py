import tkinter as tk
from .theme import theme

class IndicatorWidget(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=theme["indicator_bg"])

        self.container = tk.Frame(self, bg=self.cget('bg'))
        self.container.pack(padx=10, pady=5)

        # --- Widgets Genéricos (serão configurados pelos métodos) ---
        self.info_label = tk.Label(self.container, font=("Segoe UI", 10), fg=theme["indicator_text"], bg=self.cget('bg'))
        self.status_label = tk.Label(self.container, font=("Segoe UI", 12, "bold"), fg=theme["indicator_accent"], bg=self.cget('bg'))
        self.action_button = tk.Button(self.container, font=("Segoe UI", 9, "bold"), fg=theme["indicator_text"], relief="flat", bd=0, padx=10, pady=2)

        self.withdraw()

    def show_capture_prep(self, monitor_info, module):
        self._reset_widgets()
        self.info_label.config(text="Mire e pressione F9 para capturar. ESC para encerrar.")
        self.info_label.pack()
        self._position_and_show(monitor_info)

    def update_capture_session(self, count, module):
        self._reset_widgets()
        self.status_label.config(text=f"Capturas: {count}")
        self.action_button.config(text="CONCLUIR", bg=theme["error"], command=module.end_capture_session)

        self.status_label.pack(side="left", padx=5)
        self.action_button.pack(side="left", padx=5)

    def show_recording_prep(self, monitor_info, module):
        self._reset_widgets()
        self.status_label.config(text="Pronto para Gravar")
        self.info_label.config(text="Pressione F10 para iniciar. ESC para cancelar.")
        self.action_button.config(text="INICIAR", bg=theme["button_primary_bg"], command=module.start_recording_from_prep)

        self.status_label.pack(side="left", padx=10)
        self.info_label.pack(side="left", padx=10)
        self.action_button.pack(side="left", padx=10)
        self._position_and_show(monitor_info)

    def hide(self):
        self.withdraw()

    def _reset_widgets(self):
        for widget in self.container.winfo_children():
            widget.pack_forget()

    def _position_and_show(self, monitor_info):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        x = monitor_info['left'] + monitor_info['width'] - width - 20
        y = monitor_info['top'] + 20
        self.geometry(f"+{int(x)}+{int(y)}")
        self.deiconify()
