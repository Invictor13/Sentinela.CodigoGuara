import os
import time
import threading
import queue
from datetime import datetime
import cv2
import mss
import numpy as np
from PIL import Image
from pynput.mouse import Controller as MouseController
import tkinter as tk
import soundcard as sc
import av

from src.core.presets import get_resolved_preset, RecordingPreset
from src.utils import resource_path
from src.ui.preparation_indicator import PreparationIndicator
from src.ui.dialogs import show_success_dialog
from src.ui.preparation_mode import PreparationOverlayManager

class ScreenRecordingModule:
    def __init__(self, root, app_config):
        self.root = root
        self.app_config = app_config
        self.state = "idle"
        self.sct = mss.mss()
        self.indicator = PreparationIndicator(self.root)
        self.overlay_manager = None

        # Threading and synchronization
        self.recording_thread_obj = None
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Placeholders for recording parameters
        self.preset: RecordingPreset = None
        self.record_mic = False
        self.record_system_audio = False
        self.target_monitor = None
        self.output_filename = ""

    @property
    def is_recording(self):
        return self.state == "recording"

    @property
    def is_preparing(self):
        return self.state == "preparing"

    def enter_preparation_mode(self, record_all_screens=False):
        if self.is_recording or self.is_preparing:
            return
        self.record_all_screens = record_all_screens
        self.state = "preparing"
        self.overlay_manager = PreparationOverlayManager(
            self.root,
            self.indicator,
            indicator_text="Mire na tela e pressione F10 para Iniciar/Parar",
            inactive_text="Esta tela não será gravada."
        )
        self.overlay_manager.start()

    def start_recording_mode(self):
        if self.is_recording:
            return

        if self.is_preparing:
            if not self.overlay_manager:
                self.state = "idle"
                return
            self.target_monitor = self.overlay_manager.get_active_monitor()
            self.overlay_manager.destroy()
            self.overlay_manager = None
        else:
            self.target_monitor = self.sct.monitors[1]

        preset_key = self.app_config.get("RecordingQuality", "balanced")
        self.preset = get_resolved_preset(preset_key)
        self.record_mic = self.app_config.get("RecordMicrophone", False)
        self.record_system_audio = self.app_config.get("RecordSystemAudio", False)

        self.state = "recording"
        self.stop_event.clear()
        self.root.withdraw()
        time.sleep(0.2)

        self.recording_thread_obj = threading.Thread(target=self._recording_thread, daemon=True)
        self.recording_thread_obj.start()

        indicator_monitor = self.target_monitor or self.sct.monitors[1]
        self.indicator.show(indicator_monitor, self.stop_event)

    def stop_recording(self):
        if not self.is_recording:
            if self.is_preparing:
                self.state = "idle"
                if self.overlay_manager:
                    self.overlay_manager.destroy()
                    self.overlay_manager = None
                self.root.deiconify()
            return

        self.stop_event.set()

        if self.recording_thread_obj:
            self.recording_thread_obj.join(timeout=10)
        if self.audio_thread:
            self.audio_thread.join(timeout=5)

        self.state = "idle"
        self.indicator.hide()
        self.root.deiconify()

        def finalize():
            if os.path.exists(self.output_filename) and os.path.getsize(self.output_filename) > 0:
                show_success_dialog(self.root, "Gravação salva.", os.path.dirname(self.output_filename), self.output_filename)
            elif os.path.exists(self.output_filename):
                os.remove(self.output_filename)
        self.root.after(100, finalize)

    def _audio_capture_thread(self):
        # For simplicity, we'll handle only one audio source for now: the microphone.
        # A more complex implementation would mix or select between mic and system audio.
        device = None
        if self.record_mic:
            device = sc.default_microphone()
        elif self.record_system_audio:
            device = sc.default_speaker(include_loopback=True)

        if not device:
            return

        try:
            with device.recorder(samplerate=self.preset.audio.samplerate, channels=self.preset.audio.channels) as recorder:
                while not self.stop_event.is_set():
                    data = recorder.record(numframes=1024)
                    if data is not None:
                        self.audio_queue.put(data)
        except Exception as e:
            print(f"Erro na captura de áudio: {e}")
        finally:
            self.audio_queue.put(None) # Signal completion

    def _recording_thread(self):
        save_path = self.app_config["DefaultSaveLocation"]
        self.output_filename = os.path.join(save_path, f"Evidencia_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{self.preset.container}")

        video_settings = self.preset.video
        width, height = video_settings.resolution
        fps = video_settings.fps

        has_audio = self.record_mic or self.record_system_audio

        try:
            with av.open(self.output_filename, mode='w') as container:
                # --- Stream Setup ---
                video_stream = container.add_stream(video_settings.codec, rate=fps)
                video_stream.width = width
                video_stream.height = height
                video_stream.pix_fmt = 'yuv420p'
                video_stream.options = {'crf': str(video_settings.crf), 'preset': video_settings.preset}

                audio_stream = None
                if has_audio:
                    audio_settings = self.preset.audio
                    audio_stream = container.add_stream(audio_settings.codec, rate=audio_settings.samplerate)
                    audio_stream.bit_rate = audio_settings.bitrate
                    audio_stream.channels = audio_settings.channels

                    self.audio_queue = queue.Queue()
                    self.audio_thread = threading.Thread(target=self._audio_capture_thread, daemon=True)
                    self.audio_thread.start()

                # --- Main Recording Loop ---
                with mss.mss() as sct:
                    try:
                        cursor_img = Image.open(resource_path("cursor.png")).convert("RGBA").resize((32, 32), Image.Resampling.LANCZOS)
                    except FileNotFoundError:
                        cursor_img = None
                    mouse_controller = MouseController()

                    frame_time = 1 / fps
                    next_frame_time = time.time()
                    video_pts = 0
                    audio_pts = 0

                    while not self.stop_event.is_set():
                        loop_start_time = time.time()

                        # --- Video Frame ---
                        sct_img = sct.grab(self.target_monitor)
                        frame_bgr = np.array(sct_img)
                        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGRA2RGB)

                        # Resize if necessary
                        if (frame_rgb.shape[1], frame_rgb.shape[0]) != (width, height):
                            frame_rgb = cv2.resize(frame_rgb, (width, height), interpolation=cv2.INTER_AREA)

                        # Add cursor
                        if cursor_img:
                            frame_pil = Image.fromarray(frame_rgb)
                            mouse_pos = mouse_controller.position
                            cursor_x = mouse_pos[0] - self.target_monitor['left']
                            cursor_y = mouse_pos[1] - self.target_monitor['top']
                            scaled_cursor_x = int(cursor_x * (width / self.target_monitor['width']))
                            scaled_cursor_y = int(cursor_y * (height / self.target_monitor['height']))
                            frame_pil.paste(cursor_img, (scaled_cursor_x, scaled_cursor_y), cursor_img)
                            final_frame_rgb = np.array(frame_pil)
                        else:
                            final_frame_rgb = frame_rgb

                        video_frame = av.VideoFrame.from_ndarray(final_frame_rgb, format='rgb24')
                        video_frame.pts = video_pts
                        video_pts += 1

                        for packet in video_stream.encode(video_frame):
                            container.mux(packet)

                        # --- Audio Frames ---
                        if audio_stream:
                            try:
                                while not self.audio_queue.empty():
                                    audio_data = self.audio_queue.get_nowait()
                                    if audio_data is None: # End of stream signal
                                        break

                                    # Soundcard provides 'float32' interleaved data (num_samples, num_channels), which corresponds to the 'flt' sample format in FFmpeg/PyAV.
                                    audio_frame = av.AudioFrame.from_ndarray(
                                        audio_data,
                                        format='flt',
                                        layout= 'stereo' if audio_stream.layout.name == 'stereo' else 'mono'
                                    )
                                    audio_frame.pts = audio_pts
                                    audio_pts += audio_frame.samples

                                    for packet in audio_stream.encode(audio_frame):
                                        container.mux(packet)
                            except queue.Empty:
                                pass

                        # --- Frame Rate Control & PTS Synchronization ---
                        next_frame_time += frame_time
                        sleep_duration = next_frame_time - time.time()
                        if sleep_duration > 0:
                            time.sleep(sleep_duration)

                # --- Flush encoders ---
                for packet in video_stream.encode():
                    container.mux(packet)
                if audio_stream:
                    for packet in audio_stream.encode():
                        container.mux(packet)

        except Exception as e:
            print(f"Erro fatal no loop de gravação com PyAV: {e}")
        finally:
            if has_audio and self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=2)
            # Drain queue
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
