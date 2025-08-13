# Sentinela Guará

Uma ferramenta de gravação de tela e áudio de alta performance, forjada em Python.

## Índice

- [Funcionalidades Principais](#funcionalidades-principais)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Setup (O Ritual de Preparação da Forja)](#instalação-e-setup-o-ritual-de-preparação-da-forja)
- [Executando em Modo de Desenvolvimento](#executando-em-modo-de-desenvolvimento)
- [Compilando o Artefato (Forjando o Executável)](#compilando-o-artefato-forjando-o-executável)

## Funcionalidades Principais

- **Captura de Tela:** Inicie um modo de captura e tire múltiplas screenshots com uma única tecla de atalho.
- **Gravação de Vídeo:** Grave a tela inteira, um monitor específico ou uma janela de aplicação individual.
- **Qualidade Ajustável:** Escolha entre perfis de gravação de "Alta Qualidade" (para textos nítidos) ou "Compacta" (para compartilhamento fácil).
- **Interface Intuitiva:** Uma janela principal clara e indicadores visuais para captura e gravação.
- **Atalhos Globais:** Opere o Sentinela mesmo quando ele estiver minimizado.

## Pré-requisitos

Para começar a trabalhar no Sentinela Guará, você precisará ter o seguinte software instalado em sua máquina:

- **Python**: Versão 3.10 ou superior.
- **Git**: Para clonar o repositório do projeto.

## Instalação e Setup (O Ritual de Preparação da Forja)

Siga estes passos para configurar seu ambiente de desenvolvimento:

1.  **Clonar o Repositório**

    Abra seu terminal e clone o repositório do Sentinela Guará com o seguinte comando:

    ```bash
    git clone https://github.com/seu-usuario/sentinela-guara.git
    cd sentinela-guara
    ```
    *(Lembre-se de substituir `seu-usuario/sentinela-guara` pela URL correta do repositório.)*

2.  **Criar o Ambiente Virtual**

    É crucial criar um ambiente virtual para isolar as dependências do projeto e evitar conflitos com outros projetos Python em sua máquina. Isso garante que o projeto tenha suas próprias versões de pacotes, independentemente de outros projetos.

    ```bash
    python -m venv .venv
    ```

3.  **Ativar o Ambiente**

    Ative o ambiente virtual de acordo com o seu sistema operacional:

    -   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Instalar as Dependências**

    Com o ambiente virtual ativado, instale todas as dependências necessárias listadas no arquivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Executando em Modo de Desenvolvimento

Para rodar a aplicação diretamente do código-fonte, garantindo que todas as importações funcionem corretamente, execute o projeto como um módulo a partir do diretório raiz:

```bash
python -m src.main
```

## Compilando o Artefato (Forjando o Executável)

Para distribuir a aplicação, você pode compilá-la em um executável autônomo usando o **PyInstaller**.

1.  **Instale o PyInstaller**

    Se você ainda não o tem em seu ambiente virtual, instale-o:

    ```bash
    pip install pyinstaller
    ```

2.  **Compile o Projeto**

    Use o comando abaixo para iniciar o processo de compilação. Este comando irá agrupar seu código e dependências em uma única pasta.

    ```bash
    pyinstaller --noconfirm --windowed --name SentinelaGuara --add-data "assets;assets" --icon="assets/logo_guara.ico" src/main.py
    ```

    **Explicação das Flags:**
    - `--noconfirm`: Substitui o diretório de saída sem pedir confirmação.
    - `--windowed`: Garante que a aplicação seja executada sem um console de terminal em segundo plano.
    - `--name SentinelaGuara`: Define o nome do executável e da pasta de distribuição.
    - `--add-data "assets;assets"`: Inclui a pasta de recursos (ícones, imagens) no executável final. O caminho é especificado como `"origem;destino"`.
    - `--icon="assets/logo_guara.ico"`: Define o ícone da aplicação.

Após a compilação, o artefato final estará pronto para uso na pasta `dist/SentinelaGuara`.
