# 🅿️ OpenParking LPR - Sistema de Reconhecimento de Placas

Um sistema de Reconhecimento de Placas de Veículos (LPR) em tempo real construído com Python e tecnologias de código aberto. O sistema é capaz de capturar vídeo de uma fonte (como uma webcam), detectar veículos, reconhecer as placas e salvar as informações em um banco de dados para visualização em um dashboard web.

---

## 🛠️ Tecnologias Utilizadas

O projeto é construído com um conjunto de bibliotecas Python modernas e eficientes:

-   **Linguagem:** Python 3.11+
-   **Processamento de Imagem:** OpenCV (`opencv-python-headless`)
-   **Detecção de Objetos (Placa):** YOLOv8 (`ultralytics`)
-   **Reconhecimento de Texto (OCR):`EasyOCR (`easyocr`)
-   **Banco de Dados:** SQLite (via SQLAlchemy)
-   **Dashboard Web:** Flask
-   **Manipulação de Dados:** Pandas & Numpy

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar o OpenParking LPR em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.11 ou superior
-   `pip` (gerenciador de pacotes do Python)
-   Uma webcam conectada ou um arquivo de vídeo para teste.

### 2. Instalação das Dependências

Clone o repositório e instale as bibliotecas necessárias a partir do arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

**⚠️ Nota Importante:** Na primeira execução, as bibliotecas `ultralytics` (YOLO) e `easyocr` farão o download de seus respectivos modelos de machine learning. Isso requer uma conexão com a internet e pode levar alguns minutos.

### 3. Configuração

As configurações do sistema (URL do banco de dados, caminho do modelo, fonte da câmera, etc.) são definidas no arquivo `config.py`. Sinta-se à vontade para ajustá-las conforme suas necessidades.

### 4. Executando o Processamento LPR (main.py)

Este script é o coração do sistema. Ele ativa a câmera, processa o vídeo e salva as detecções.

-   Abra um terminal na raiz do projeto.
-   Execute o seguinte comando:

```bash
python main.py
```

-   Uma janela de vídeo será aberta, mostrando o feed da sua câmera. Aponte-a para uma placa de veículo.
-   As placas reconhecidas e validadas serão exibidas no terminal e salvas no banco de dados.
-   **Funcionalidade de Deduplicação:** O sistema agora evita o registro de placas duplicadas no banco de dados se a mesma placa for detectada novamente dentro de um período de 1 minuto.
-   Para encerrar, pressione a tecla **`q`** com a janela de vídeo em foco.

### 5. Visualizando o Dashboard Web (app.py)

Para ver as placas salvas através de uma interface web, execute o aplicativo Flask.

-   Abra um **novo terminal**.
-   Execute o comando:

```bash
python app.py
```

-   Seu navegador será aberto no endereço `http://127.0.0.1:5001`, mostrando o painel com as detecções.
-   Você pode executar os dois scripts (`main.py` e `app.py`) simultaneamente para ver os resultados em tempo real (atualize a página do navegador para ver os dados mais recentes).

---

## 🐳 Containerização com Docker

Para uma execução mais isolada e consistente, você pode usar Docker:

1.  **Construir a imagem Docker:**
    ```bash
    docker build -t openparking-lpr .
    ```
2.  **Executar o contêiner:**
    ```bash
    docker run -p 5001:5001 openparking-lpr
    ```
    (Se você quiser executar o `main.py` no contêiner, precisará de acesso à webcam, o que requer configurações adicionais de Docker.)

---

## 🎯 Precisão do Modelo

O sistema utiliza o modelo `yolov8n.pt` por padrão, que é um modelo de detecção de objetos genérico. Para obter uma alta precisão na **detecção de placas de veículos**, é altamente recomendável substituí-lo por um modelo YOLO treinado especificamente para essa tarefa. Você pode treinar o seu próprio modelo ou encontrar modelos pré-treinados na comunidade.
