# Este é o grimório comum, um lugar para feitiços e utilitários compartilhados.
import sys
import os
import logging
from screeninfo import get_monitors

def resource_path(relative_path):
    """ Obtém o caminho absoluto para um recurso, funciona para dev e para o PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver no modo PyInstaller, use o caminho do arquivo
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, "assets", relative_path)

def get_primary_monitor_resolution():
    """Retorna a resolução (largura, altura) do monitor primário."""
    try:
        primary_monitor = next(m for m in get_monitors() if m.is_primary)
        return (primary_monitor.width, primary_monitor.height)
    except StopIteration:
        # Fallback se nenhum monitor for marcado como primário
        logging.warning("Nenhum monitor primário detectado. Usando o primeiro monitor da lista.")
        if get_monitors():
            monitor = get_monitors()[0]
            return (monitor.width, monitor.height)
        return (1920, 1080) # Fallback absoluto

def get_primary_monitor_refresh_rate():
    """
    Tenta obter a taxa de atualização do monitor primário.
    Atualmente, nenhuma biblioteca de plataforma cruzada confiável em Python
    fornece essa informação de forma consistente.
    Retorna um padrão seguro de 60 FPS.
    """
    logging.warning("A detecção da taxa de atualização do monitor não é suportada. Usando o padrão de 60 FPS.")
    return 60
