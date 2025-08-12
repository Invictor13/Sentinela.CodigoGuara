from dataclasses import dataclass, field, replace
from src.utils import get_primary_monitor_resolution, get_primary_monitor_refresh_rate
import logging

@dataclass
class AudioSettings:
    """Configurações de áudio para um preset."""
    codec: str
    bitrate: str
    channels: int = 2
    samplerate: int = 48000

@dataclass
class VideoSettings:
    """Configurações de vídeo para um preset."""
    codec: str
    resolution: tuple[int, int]
    fps: int
    crf: int = 23
    preset: str = 'medium'

@dataclass
class RecordingPreset:
    """Define um preset de gravação completo."""
    name: str
    container: str
    video: VideoSettings
    audio: AudioSettings
    is_native: bool = False # Flag to indicate if this preset uses native settings

def _get_limited_resolution(max_width, max_height):
    """Limita a resolução nativa a um máximo, mantendo o aspect ratio."""
    try:
        native_width, native_height = get_primary_monitor_resolution()
    except Exception as e:
        logging.error(f"Não foi possível obter a resolução nativa, usando 1920x1080 como fallback. Erro: {e}")
        native_width, native_height = 1920, 1080

    if native_width <= max_width and native_height <= max_height:
        return (native_width, native_height)

    aspect_ratio = native_width / native_height
    if (native_width / max_width) > (native_height / max_height):
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    if new_width % 2 != 0: new_width -= 1
    if new_height % 2 != 0: new_height -= 1

    return (new_width, new_height)

# --- Definição dos Presets BASE ---
# Usamos placeholders (0,0) e 0 para resolução/fps nativos

PRESET_HIGH = RecordingPreset(
    name="Alta Qualidade (Nativa)",
    container=".mp4",
    is_native=True,
    video=VideoSettings(
        codec='libx264',
        resolution=(0, 0), # Placeholder
        fps=0, # Placeholder
        crf=18,
        preset='ultrafast'
    ),
    audio=AudioSettings(codec='aac', bitrate='320k')
)

PRESET_BALANCED = RecordingPreset(
    name="Balanceado (1080p MP4)",
    container=".mp4",
    video=VideoSettings(
        codec='libx264',
        resolution=_get_limited_resolution(1920, 1080),
        fps=30,
        crf=23,
        preset='medium'
    ),
    audio=AudioSettings(codec='aac', bitrate='192k')
)

PRESET_COMPACT = RecordingPreset(
    name="Compacto (720p WebM)",
    container=".webm",
    video=VideoSettings(
        codec='libvpx-vp9',
        resolution=_get_limited_resolution(1280, 720),
        fps=24,
        crf=32,
        preset='medium'
    ),
    audio=AudioSettings(codec='libopus', bitrate='96k')
)

# --- Dicionário para fácil acesso ---

RECORDING_PRESETS = {
    "high": PRESET_HIGH,
    "balanced": PRESET_BALANCED,
    "compact": PRESET_COMPACT
}

PRESET_OPTIONS_ORDER = ["high", "balanced", "compact"]
PRESET_DISPLAY_NAMES = [p.name for p in RECORDING_PRESETS.values()]

def get_resolved_preset(key: str) -> RecordingPreset:
    """
    Retorna uma cópia do preset com os valores nativos resolvidos no momento da chamada.
    """
    base_preset = RECORDING_PRESETS.get(key)
    if not base_preset:
        logging.error(f"Preset '{key}' não encontrado. Usando 'balanced' como fallback.")
        base_preset = RECORDING_PRESETS["balanced"]

    if base_preset.is_native:
        # Cria uma nova cópia do preset para não modificar o original
        resolved_preset = replace(base_preset)
        try:
            native_resolution = get_primary_monitor_resolution()
            native_fps = get_primary_monitor_refresh_rate()
            resolved_preset.video.resolution = native_resolution
            resolved_preset.video.fps = native_fps
        except Exception as e:
            logging.error(f"Falha ao resolver preset nativo, usando 1920x1080@60fps. Erro: {e}")
            resolved_preset.video.resolution = (1920, 1080)
            resolved_preset.video.fps = 60
        return resolved_preset

    return base_preset
