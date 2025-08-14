import sys
from pystray import MenuItem as item, Icon as icon, Menu
from PIL import Image
import os

from src.utils import resource_path
from src.ui.theme import theme

def setup_tray_icon(root, capture_module, recording_module, app_config):

    def quit_application(icon_instance):
        icon_instance.stop()
        root.quit()
        sys.exit()

    def show_main_window():
        root.deiconify()
        root.lift()
        root.focus_force()

    def open_evidence_folder():
        folder_to_open = app_config["DefaultSaveLocation"]
        try:
            os.startfile(folder_to_open)
        except Exception as e:
            print(f"Não foi possível abrir a pasta de evidências: {e}")

    try:
        image = Image.open(resource_path("assets/sentinela.ico"))
    except FileNotFoundError:
        # Create a placeholder image with the primary theme color
        image = Image.new('RGB', (64, 64), color = theme["primary"])

    menu = (
        item('Exibir Sentinela', show_main_window, default=True),
        Menu.SEPARATOR,
        item('Capturar Tela (Shift+F9)', lambda: root.after(0, capture_module.start_capture_mode)),
        item('Gravar Vídeo (Shift+F10)', lambda: root.after(0, recording_module.open_recording_selection_ui)),
        item('Abrir Pasta de Evidências', open_evidence_folder),
        Menu.SEPARATOR,
        item('Sair', quit_application)
    )

    icon_instance = icon("Sentinela Guará", image, "Sentinela Guará", menu)
    icon_instance.run()
