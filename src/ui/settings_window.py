import tkinter as tk
from tkinter import Toplevel, filedialog, messagebox, ttk
import os
from tkinter import font as tkfont

from src.config.settings import save_app_config
from src.core.presets import PRESET_DISPLAY_NAMES, PRESET_OPTIONS_ORDER

COR_FUNDO_JANELA = "#f0f5f0"
COR_TEXTO_PRINCIPAL = "#005a36"
COR_TEXTO_SECUNDARIO = "#555555"

class SettingsWindow(Toplevel):
    def __init__(self, parent, app_config, on_close_callback=None, is_first_run=False):
        super().__init__(parent)
        self.app_config = app_config
        self.on_close_callback = on_close_callback
        self.is_first_run = is_first_run

        self.title("Configurações do Sentinela Guará")
        self.geometry("520x550")
        self.configure(bg=COR_FUNDO_JANELA)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.wm_attributes("-topmost", True)

        main_frame = tk.Frame(self, bg=COR_FUNDO_JANELA, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        current_row = 0

        if self.is_first_run:
            # ... (código da primeira execução mantido)
            current_row += 2

        title_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        # --- Recording Quality ---
        tk.Label(main_frame, text="Qualidade da Gravação", font=title_font, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_PRINCIPAL).grid(row=current_row, column=0, columnspan=3, sticky="w", pady=(0, 5))
        current_row += 1

        self.quality_var = tk.StringVar(value=self.app_config.get("RecordingQuality", "balanced"))

        # Mapeia o valor salvo (e.g., 'high') para o índice da lista de exibição
        current_quality_index = PRESET_OPTIONS_ORDER.index(self.quality_var.get())

        self.quality_combo = ttk.Combobox(main_frame, values=PRESET_DISPLAY_NAMES, state="readonly", width=40)
        self.quality_combo.grid(row=current_row, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        self.quality_combo.current(current_quality_index)
        current_row += 1

        ttk.Separator(main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=3, sticky='ew', pady=15)
        current_row += 1

        # --- Audio Settings ---
        tk.Label(main_frame, text="Fontes de Áudio", font=title_font, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_PRINCIPAL).grid(row=current_row, column=0, columnspan=3, sticky="w", pady=(0, 5))
        current_row += 1

        self.record_mic_var = tk.BooleanVar(value=self.app_config.get("RecordMicrophone", False))
        self.record_system_audio_var = tk.BooleanVar(value=self.app_config.get("RecordSystemAudio", False))

        audio_frame = tk.Frame(main_frame, bg=COR_FUNDO_JANELA)
        audio_frame.grid(row=current_row, column=0, columnspan=3, sticky="w", padx=20)
        current_row += 1

        style = ttk.Style()
        style.configure("TCheckbutton", background=COR_FUNDO_JANELA, foreground=COR_TEXTO_SECUNDARIO)

        ttk.Checkbutton(audio_frame, text="Gravar Microfone", variable=self.record_mic_var, style="TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(audio_frame, text="Gravar Áudio do Sistema (Loopback)", variable=self.record_system_audio_var, style="TCheckbutton").pack(anchor="w")

        ttk.Separator(main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=3, sticky='ew', pady=15)
        current_row += 1

        # --- Hotkeys and Save Path (mantidos como antes) ---
        # ... (código dos atalhos e caminho de salvar)
        tk.Label(main_frame, text="Atalhos", font=title_font, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_PRINCIPAL).grid(row=current_row, column=0, columnspan=3, sticky="w", pady=(0, 10))
        current_row += 1
        tk.Label(main_frame, text="Captura de Tela:", font=("Segoe UI", 10), bg=COR_FUNDO_JANELA, fg=COR_TEXTO_SECUNDARIO).grid(row=current_row, column=0, sticky="w", pady=(0, 5))
        self.capture_hotkey_var = tk.StringVar(value=self.app_config.get("CaptureHotkey", "F9"))
        tk.Entry(main_frame, textvariable=self.capture_hotkey_var, state="readonly", width=20).grid(row=current_row, column=1, sticky="ew", padx=5)
        current_row += 1
        tk.Label(main_frame, text="Gravação de Vídeo:", font=("Segoe UI", 10), bg=COR_FUNDO_JANELA, fg=COR_TEXTO_SECUNDARIO).grid(row=current_row, column=0, sticky="w", pady=(0, 5))
        self.record_hotkey_var = tk.StringVar(value=self.app_config.get("RecordHotkey", "F10"))
        tk.Entry(main_frame, textvariable=self.record_hotkey_var, state="readonly", width=20).grid(row=current_row, column=1, sticky="ew", padx=5)
        current_row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=3, sticky='ew', pady=15)
        current_row += 1
        tk.Label(main_frame, text="Pasta Padrão", font=title_font, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_PRINCIPAL).grid(row=current_row, column=0, sticky="w", pady=(0, 5))
        current_row += 1
        self.save_path_var = tk.StringVar(value=self.app_config["DefaultSaveLocation"])
        tk.Entry(main_frame, textvariable=self.save_path_var, state="readonly").grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        browse_button = tk.Button(main_frame, text="Procurar...", command=self.browse_save_path, font=("Segoe UI", 9))
        browse_button.grid(row=current_row, column=2, padx=(5, 0))
        current_row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=3, sticky='ew', pady=15)
        current_row += 1

        # --- Save Button ---
        buttons_frame = tk.Frame(main_frame, bg=COR_FUNDO_JANELA)
        buttons_frame.grid(row=current_row, column=0, columnspan=3, pady=(20,0))
        tk.Button(buttons_frame, text="Salvar Configurações", command=self.save_settings, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Button(buttons_frame, text="Fechar", command=self.destroy, font=("Segoe UI", 10)).pack(side="left", padx=10)
        main_frame.columnconfigure(1, weight=1)

    def browse_save_path(self):
        new_path = filedialog.askdirectory(initialdir=self.save_path_var.get(), parent=self)
        if new_path:
            self.save_path_var.set(new_path)

    def save_settings(self):
        # Get selected quality from combobox index
        selected_quality_index = self.quality_combo.current()
        new_quality_key = PRESET_OPTIONS_ORDER[selected_quality_index]

        new_record_mic = self.record_mic_var.get()
        new_record_system_audio = self.record_system_audio_var.get()
        new_save_path = self.save_path_var.get()
        new_capture_hotkey = self.capture_hotkey_var.get()
        new_record_hotkey = self.record_hotkey_var.get()

        try:
            os.makedirs(new_save_path, exist_ok=True)
            with open(os.path.join(new_save_path, ".test"), "w") as f: f.write("test")
            os.remove(os.path.join(new_save_path, ".test"))
        except OSError:
            messagebox.showerror("Erro de Caminho", "Não foi possível escrever no caminho especificado.", parent=self)
            return

        config_parser_obj = self.app_config["config_parser_obj"]
        if self.is_first_run:
            if not config_parser_obj.has_section('User'): config_parser_obj.add_section('User')
            config_parser_obj.set('User', 'has_run_before', 'true')

        save_app_config(
            config_parser_obj,
            new_save_path,
            new_quality_key,
            new_capture_hotkey,
            new_record_hotkey,
            new_record_mic,
            new_record_system_audio
        )

        # Update the live app_config dictionary
        self.app_config["DefaultSaveLocation"] = new_save_path
        self.app_config["RecordingQuality"] = new_quality_key
        self.app_config["RecordMicrophone"] = new_record_mic
        self.app_config["RecordSystemAudio"] = new_record_system_audio
        self.app_config["CaptureHotkey"] = new_capture_hotkey
        self.app_config["RecordHotkey"] = new_record_hotkey
        self.app_config["HasRunBefore"] = True

        if self.on_close_callback:
            self.on_close_callback(new_save_path)

        messagebox.showinfo("Sucesso", "Configurações salvas.", parent=self)
        self.destroy()
