import tkinter as tk
from tkinter import Toplevel
from .theme import theme

class PreparationIndicator(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.animation_id = None
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.withdraw()
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.active_monitor_for_recording = None # Legacy for `show` method

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_preparation_mode(self, monitor_geom, text=""):
        self._clear_container()
        self.container.configure(bg=theme["indicator_bg"], padx=10, pady=5)

        prep_label = tk.Label(self.container, text="● Preparando", font=("Segoe UI", 12, "bold"), fg=theme["preparation_text"], bg=self.container.cget('bg'))
        prep_label.pack(side="left", padx=(0, 10))

        info_label = tk.Label(self.container, text=text, font=("Segoe UI", 10), fg=theme["indicator_text"], bg=self.container.cget('bg'))
        info_label.pack(side="left", padx=(0, 15))

        self._display_window(monitor_geom)

    def hide_preparation_mode(self):
        self.withdraw()

    def flash_success(self):
        """Flashes the indicator green to show a successful capture."""
        if not self.winfo_exists():
            return

        original_bg = self.container.cget('bg')
        original_prep_fg = self.container.winfo_children()[0].cget('fg') # Assuming first child is the "● Preparando" label

        success_color = theme["success"]
        self.container.configure(bg=success_color)
        for widget in self.container.winfo_children():
            widget.configure(bg=success_color)

        def restore_colors():
            if self.winfo_exists():
                self.container.configure(bg=original_bg)
                # Restore original colors of all children
                self.container.winfo_children()[0].configure(fg=original_prep_fg, bg=original_bg)
                for child in self.container.winfo_children()[1:]:
                    child.configure(bg=original_bg)

        self.after(150, restore_colors)

    def _display_window(self, monitor_geom):
        if not monitor_geom: return
        self.update_idletasks()
        x = monitor_geom['left'] + monitor_geom['width'] - self.winfo_reqwidth() - 20
        y = monitor_geom['top'] + 20
        self.geometry(f"+{x}+{y}")
        self.deiconify()

    def hide(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.animation_id = None
        self.withdraw()

    # --- Legacy methods for ScreenRecordingModule ---
    # This part remains to avoid breaking the recording functionality,
    # but ideally, it would be in its own `RecordingStateIndicator` class.

    def show(self, monitor_geom, stop_event):
        """ Mostra o indicador no modo de gravação normal. """
        self.stop_event = stop_event
        self._clear_container()
        self.container.configure(bg=theme["indicator_bg"], padx=10, pady=5)

        self.rec_label = tk.Label(self.container, text="REC", font=("Segoe UI", 12, "bold"), fg=theme["recording_dot"], bg=self.container.cget('bg'))
        self.rec_label.pack(side="left", padx=(0, 10))

        self.time_label = tk.Label(self.container, text="00:00:00", font=("Segoe UI", 12, "bold"), fg=theme["indicator_text"], bg=self.container.cget('bg'))
        self.time_label.pack(side="left", padx=(0, 10))

        self.info_label = tk.Label(self.container, text="F10 para parar", font=("Segoe UI", 10), fg=theme["indicator_text"], bg=self.container.cget('bg'))
        self.info_label.pack(side="left", padx=(0, 15))

        self._display_window(monitor_geom)
        self.update_time_async() # Inicia o cronômetro
        self._animate_rec_async() # Inicia a animação

    def _animate_rec_async(self):
        # Correcting indentation and ensuring the stop event is checked properly.
        if not self.winfo_exists() or self.stop_event.is_set():
            if self.animation_id:
                self.after_cancel(self.animation_id)
                self.animation_id = None
            return

        current_color = self.rec_label.cget("fg")
        new_color = self.cget('bg') if current_color == theme["recording_dot"] else theme["recording_dot"]
        self.rec_label.config(fg=new_color)
        self.animation_id = self.after(700, self._animate_rec_async)

    def update_time(self, elapsed_seconds):
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            secs = int(elapsed_seconds)
            mins, secs = divmod(secs, 60)
            hrs, mins = divmod(mins, 60)
            self.time_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")

    def update_time_async(self):
        self.start_time = time.time()

        def update():
            if self.winfo_exists() and not self.stop_event.is_set():
                elapsed = time.time() - self.start_time
                self.update_time(elapsed)
                self.after(1000, update)

        self.update_time(0)
        update()
