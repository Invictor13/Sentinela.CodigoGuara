# Paleta de Cores Oficial da Código Guará
LARANJA_GUARA = "#e67e22"  # Primária
CINZA_ROCHA = "#34495e"  # Secundária
NEGRO_NOTURNO = "#2c3e50"  # Texto Principal
BRANCO_NEVE = "#ecf0f1"  # Fundo
VERDE_CURA = "#2ecc71"  # Sucesso
VERMELHO_ALERTA = "#e74c3c"  # Erro

# Mapeamento Semântico de Cores (Tema da Aplicação)
theme = {
    "primary": LARANJA_GUARA,
    "secondary": CINZA_ROCHA,
    "text": NEGRO_NOTURNO,
    "background": BRANCO_NEVE,
    "success": VERDE_CURA,
    "error": VERMELHO_ALERTA,

    # Mapeamentos específicos da UI do Sentinela
    "window_bg": BRANCO_NEVE,
    "card_bg": "#ffffff", # Um branco puro para os cards se destacarem do fundo
    "text_primary": NEGRO_NOTURNO,
    "text_secondary": "#7f8c8d", # Um cinza suave para texto de apoio
    "button_primary_bg": LARANJA_GUARA,
    "button_primary_hover": "#d35400", # Laranja mais escuro para hover
    "button_secondary_bg": CINZA_ROCHA,
    "button_secondary_hover": "#2c3e50", # Cinza mais escuro para hover
    "separator": "#bdc3c7", # Cinza claro para linhas separadoras

    # Cores para indicadores e status
    "indicator_bg": "#2c3e50", # Usando o Negro Noturno para um look "pro"
    "indicator_text": BRANCO_NEVE,
    "indicator_accent": LARANJA_GUARA,
    "recording_dot": VERMELHO_ALERTA,
    "preparation_text": "#f1c40f" # Um amarelo para o estado de preparação
}
