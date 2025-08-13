import tkinter as tk
from tkinter import Toplevel
from datetime import datetime, timedelta
from .theme import theme

class PreparationIndicator(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.animation_id = None
        self._timer_job = None
        self.start_time = None
        self.stop_event = None

        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.withdraw()

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _display_window(self, monitor_geom):
        if not monitor_geom: return
        self.update_idletasks()
        x = monitor_geom['left'] + monitor_geom['width'] - self.winfo_reqwidth() - 20
        y = monitor_geom['top'] + 20
        self.geometry(f"+{x}+{y}")
        self.deiconify()

    def hide(self):
        # Cancel any pending animation or timer jobs to prevent background processing
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None
        self.withdraw()

    # --- ScreenRecordingModule specific methods ---

    def show(self, monitor_geom, stop_event):
        """Prepares and shows the indicator for recording mode."""
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

        # Start the timer and animation loops
        self.start_time = datetime.now()
        self._update_timer()
        self._animate_rec()

    def _animate_rec(self):
        """Animates the 'REC' label by toggling its color."""
        if not self.winfo_exists() or (self.stop_event and self.stop_event.is_set()):
            if self.animation_id:
                self.after_cancel(self.animation_id)
                self.animation_id = None
            return

        current_color = self.rec_label.cget("fg")
        new_color = self.container.cget('bg') if current_color == theme["recording_dot"] else theme["recording_dot"]
        self.rec_label.config(fg=new_color)

        self.animation_id = self.after(700, self._animate_rec)

    def _update_timer(self):
        """The core timer loop. Calculates elapsed time, updates the label, and reschedules itself."""
        if not self.winfo_exists() or (self.stop_event and self.stop_event.is_set()):
            if self._timer_job:
                self.after_cancel(self._timer_job)
                self._timer_job = None
            return

        elapsed_delta = datetime.now() - self.start_time

        # Format timedelta to HH:MM:SS
        total_seconds = int(elapsed_delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.time_label.config(text=time_str)

        self._timer_job = self.after(1000, self._update_timer)

    # --- Legacy/Other methods ---
    # These methods are not directly part of the recording timer but are kept for other functionalities.

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
        original_prep_fg = self.container.winfo_children()[0].cget('fg')

        success_color = theme["success"]
        self.container.configure(bg=success_color)
        for widget in self.container.winfo_children():
            widget.configure(bg=success_color)

        def restore_colors():
            if self.winfo_exists():
                self.container.configure(bg=original_bg)
                self.container.winfo_children()[0].configure(fg=original_prep_fg, bg=original_bg)
                for child in self.container.winfo_children()[1:]:
                    child.configure(bg=original_bg)

        self.after(150, restore_colors)
