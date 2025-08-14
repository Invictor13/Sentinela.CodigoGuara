# Sentinela Guará

Uma ferramenta de gravação de tela e áudio de alta performance, forjada em Python.

## Índice

- [Funcionalidades Principais](#funcionalidades-principais)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Setup (O Caminho do Mestre)](#instalação-e-setup-o-caminho-do-mestre)
- [Executando em Modo de Desenvolvimento](#executando-em-modo-de-desenvolvimento)
- [Compilando o Artefato (O Ritual de Batalha Final)](#compilando-o-artefato-o-ritual-de-batalha-final)
- [Notas da Forja (Solução de Problemas Comuns)](#notas-da-forja-solução-de-problemas-comuns)

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

## Instalação e Setup (O Caminho do Mestre)

Siga estes passos para configurar seu ambiente de desenvolvimento:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/sentinela-guara.git
    ```
    *(Lembre-se de substituir `seu-usuario/sentinela-guara` pela URL correta do repositório.)*

2.  **Navegue até a pasta:**
    ```bash
    cd Sentinela.CodigoGuara-main
    ```

3.  **Crie o Santuário Virtual:**
    ```bash
    python -m venv .venv
    ```

4.  **Instale os Ingredientes Essenciais (Requisitos):**
    Use o Feitiço de Invocação Direta, que é imune aos escudos de proteção do PowerShell. Este método garante que você está usando o interpretador Python e o gerenciador de pacotes do seu ambiente virtual, sem a necessidade de ativá-lo explicitamente.
    ```bash
    bash .venv\Scripts\python.exe -m pip install -r requirements.txt
    ```

## Executando em Modo de Desenvolvimento

Para rodar a aplicação diretamente do código-fonte, utilize o método de "Invocação Direta" para garantir que o interpretador correto do ambiente virtual seja usado:

```bash
bash .venv\Scripts\python.exe -m src.main
```

## Compilando o Artefato (O Ritual de Batalha Final)

Para distribuir a aplicação, você pode compilá-la em um executável autônomo.

1.  **Forje o Martelo de Compilação (PyInstaller):**
    Primeiro, instale o PyInstaller no seu ambiente virtual usando a "Invocação Direta".
    ```bash
    bash .venv\Scripts\python.exe -m pip install pyinstaller
    ```

2.  **Conjurando o Encantamento de Vinculação Final:**
    Execute o comando a seguir para compilar o projeto. Ele irá agrupar o código e todas as dependências em uma única pasta.
    ```bash
    bash .venv\Scripts\pyinstaller.exe --noconfirm --windowed --name SentinelaGuara --icon="assets/sentinela.ico" --add-data "assets;assets/" src/main.py
    ```

3.  **O Artefato Final:**
    Após a conclusão do ritual, o executável e todos os seus arquivos de suporte estarão localizados na pasta `dist/SentinelaGuara`, prontos para a batalha.

## Notas da Forja (Solução de Problemas Comuns)

-   **O Fantasma do Ícone (Cache do Windows):**
    O Windows armazena ícones de aplicativos em um cache para acelerar sua exibição. Após recompilar o Sentinela Guará com um novo ícone, o sistema operacional pode continuar exibindo o ícone antigo. Para forçar a atualização, execute o 'Ritual de Expurgo do Cache'. Abra o `cmd` como administrador e execute os seguintes comandos em sequência:
    ```cmd
    ie4uinit.exe -show
    taskkill /IM explorer.exe /F
    DEL "%localappdata%\IconCache.db" /A
    explorer.exe
    ```

-   **Conflitos com a Biblioteca Imperial (Erros de Pacotes Globais):**
    O método de 'Invocação Direta' (`bash .venv\Scripts\python.exe ...`) é uma salvaguarda poderosa. Ele garante que seu comando está usando o interpretador Python e os pacotes instalados dentro do "Santuário Virtual" (`.venv`), ignorando qualquer versão do Python ou pacotes conflitantes que possam estar instalados globalmente em seu sistema. Isso evita uma classe comum de erros onde o sistema tenta usar uma versão de biblioteca incompatível.
