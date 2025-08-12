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
from tkinter import messagebox
import soundcard as sc
import ffmpeg

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
        self.audio_threads = []
        self.audio_queues = []
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

    def enter_preparation_mode(self):
        if self.is_recording or self.is_preparing:
            return
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
        else: # Direct start (e.g., record all screens in future)
            self.target_monitor = self.sct.monitors[1]

        # Load settings from app_config
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

        # Wait for threads to finish
        if self.recording_thread_obj:
            self.recording_thread_obj.join(timeout=5)
        for t in self.audio_threads:
            t.join(timeout=3)

        self.state = "idle"
        self.indicator.hide()
        self.root.deiconify()

        # Finalize on main thread to avoid Tkinter issues
        def finalize():
            if os.path.exists(self.output_filename) and os.path.getsize(self.output_filename) > 0:
                show_success_dialog(self.root, "Gravação salva.", os.path.dirname(self.output_filename), self.output_filename)
            elif os.path.exists(self.output_filename):
                os.remove(self.output_filename) # Remove empty file on error
        self.root.after(100, finalize)

    def _audio_capture_thread(self, audio_queue: queue.Queue, is_mic: bool):
        try:
            if is_mic:
                # Get default microphone
                device = sc.default_microphone()
            else:
                # Get default speaker (loopback)
                device = sc.default_speaker()

            with device.recorder(samplerate=self.preset.audio.samplerate, channels=self.preset.audio.channels) as recorder:
                while not self.stop_event.is_set():
                    data = recorder.record(numframes=1024)
                    if data is not None:
                        audio_queue.put(data.tobytes())
        except Exception as e:
            print(f"Erro na captura de áudio ({'mic' if is_mic else 'loopback'}): {e}")
            # Signal that this audio stream is dead
            audio_queue.put(None)

    def _recording_thread(self):
        save_path = self.app_config["DefaultSaveLocation"]
        self.output_filename = os.path.join(save_path, f"Evidencia_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{self.preset.container}")

        # --- Setup Video Stream ---
        video_settings = self.preset.video
        width, height = video_settings.resolution

        video_input = ffmpeg.input(
            'pipe:',
            format='rawvideo',
            pix_fmt='bgr24', # OpenCV uses BGR
            s=f'{width}x{height}',
            r=video_settings.fps
        )

        # --- Setup Audio Streams ---
        self.audio_queues = []
        self.audio_threads = []
        audio_inputs = []

        if self.record_mic:
            mic_q = queue.Queue()
            self.audio_queues.append(mic_q)
            mic_thread = threading.Thread(target=self._audio_capture_thread, args=(mic_q, True), daemon=True)
            self.audio_threads.append(mic_thread)
            audio_inputs.append(ffmpeg.input('pipe:', format='f32le', ar=str(self.preset.audio.samplerate), ac=self.preset.audio.channels))

        if self.record_system_audio:
            sys_q = queue.Queue()
            self.audio_queues.append(sys_q)
            sys_thread = threading.Thread(target=self._audio_capture_thread, args=(sys_q, False), daemon=True)
            self.audio_threads.append(sys_thread)
            audio_inputs.append(ffmpeg.input('pipe:', format='f32le', ar=str(self.preset.audio.samplerate), ac=self.preset.audio.channels))

        # Start audio capture
        for t in self.audio_threads:
            t.start()

        # --- Configure FFmpeg Process ---
        streams = [video_input]
        if audio_inputs:
            # If there's audio, mix it
            if len(audio_inputs) > 1:
                mixed_audio = ffmpeg.filter(audio_inputs, 'amix', inputs=len(audio_inputs))
                streams.append(mixed_audio)
            else:
                streams.extend(audio_inputs)

        process = (
            ffmpeg.output(
                *streams,
                self.output_filename,
                vcodec=video_settings.codec,
                pix_fmt='yuv420p', # Common pixel format for compatibility
                preset=video_settings.preset,
                crf=video_settings.crf,
                acodec=self.preset.audio.codec,
                audio_bitrate=self.preset.audio.bitrate,
                r=video_settings.fps,
                **{'g': video_settings.fps * 2} # GOP size
            )
            .overwrite_output()
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        # --- Main Recording Loop ---
        try:
            with mss.mss() as sct:
                # Load cursor image once
                try:
                    cursor_img = Image.open(resource_path("cursor.png")).convert("RGBA").resize((32, 32), Image.Resampling.LANCZOS)
                except FileNotFoundError:
                    cursor_img = None
                mouse_controller = MouseController()

                while not self.stop_event.is_set():
                    loop_start_time = time.time()

                    # Capture video frame
                    sct_img = sct.grab(self.target_monitor)
                    frame_np = np.array(sct_img)

                    # Resize if necessary
                    if (frame_np.shape[1], frame_np.shape[0]) != (width, height):
                        frame_np = cv2.resize(frame_np, (width, height), interpolation=cv2.INTER_AREA)

                    # Add cursor
                    if cursor_img:
                        frame_pil = Image.fromarray(cv2.cvtColor(frame_np, cv2.COLOR_BGRA2RGB))
                        mouse_pos = mouse_controller.position
                        cursor_x = mouse_pos[0] - self.target_monitor['left']
                        cursor_y = mouse_pos[1] - self.target_monitor['top']
                        scaled_cursor_x = int(cursor_x * (width / self.target_monitor['width']))
                        scaled_cursor_y = int(cursor_y * (height / self.target_monitor['height']))
                        frame_pil.paste(cursor_img, (scaled_cursor_x, scaled_cursor_y), cursor_img)
                        final_frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
                    else:
                        final_frame = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)

                    # Write video frame to ffmpeg stdin
                    process.stdin.write(final_frame.tobytes())

                    # Write audio frames
                    for i, q in enumerate(self.audio_queues):
                        try:
                            while not q.empty():
                                audio_data = q.get_nowait()
                                if audio_data:
                                    process.stdin.write(audio_data)
                        except queue.Empty:
                            continue

                    # Frame rate control
                    sleep_time = (1 / video_settings.fps) - (time.time() - loop_start_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        except Exception as e:
            print(f"Erro fatal no loop de gravação: {e}")
        finally:
            # --- Cleanup ---
            process.stdin.close()
            process.wait()
            # Drain audio queues
            for q in self.audio_queues:
                while not q.empty():
                    q.get_nowait()
