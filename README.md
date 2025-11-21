# 🅿️ OpenParking LPR - Sistema de Reconhecimento de Placas

Um sistema de Reconhecimento de Placas de Veículos (LPR) em tempo real construído com Python e tecnologias de código aberto. O sistema é capaz de capturar vídeo de uma fonte (como uma webcam), detectar veículos, reconhecer as placas e salvar as informações em um banco de dados para visualização em um dashboard web.

---

## 🛠️ Tecnologias Utilizadas

O projeto é construído com um conjunto de bibliotecas Python modernas e eficientes:

-   **Linguagem:** Python 3.10+
-   **Processamento de Imagem:** OpenCV (`opencv-python-headless`)
-   **Detecção de Objetos (Placa):** YOLOv8 (`ultralytics`)
-   **Reconhecimento de Texto (OCR):** EasyOCR (`easyocr`)
-   **Banco de Dados:** SQLite (via SQLAlchemy)
-   **Dashboard Web:** Streamlit
-   **Manipulação de Dados:** Pandas & Numpy

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar o OpenParking LPR em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.10 ou superior
-   `pip` (gerenciador de pacotes do Python)
-   Uma webcam conectada ou um arquivo de vídeo para teste.

### 2. Instalação das Dependências

Clone o repositório e instale as bibliotecas necessárias a partir do arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

**⚠️ Nota Importante:** Na primeira execução, as bibliotecas `ultralytics` (YOLO) e `easyocr` farão o download de seus respectivos modelos de machine learning. Isso requer uma conexão com a internet e pode levar alguns minutos.

### 3. Executando o Processamento LPR

Este script é o coração do sistema. Ele ativa a câmera, processa o vídeo e salva as detecções.

-   Abra um terminal na raiz do projeto.
-   Execute o seguinte comando:

```bash
python main.py
```

-   Uma janela de vídeo será aberta, mostrando o feed da sua câmera. Aponte-a para uma placa de veículo.
-   As placas reconhecidas e validadas serão exibidas no terminal e salvas no banco de dados.
-   Para encerrar, pressione a tecla **`q`** com a janela de vídeo em foco.

### 4. Visualizando o Dashboard

Para ver as placas salvas, execute o dashboard Streamlit.

-   Abra um **novo terminal**.
-   Execute o comando:

```bash
streamlit run app.py
```

-   Seu navegador será aberto no endereço `http://localhost:8501`, mostrando o painel com as detecções.
-   Você pode executar os dois scripts (`main.py` e `app.py`) simultaneamente para ver os resultados em tempo real (lembre-se de clicar em "Atualizar Dados" no dashboard).

---

## 🎯 Precisão do Modelo

O sistema utiliza o modelo `yolov8n.pt` por padrão, que é um modelo de detecção de objetos genérico. Para obter uma alta precisão na **detecção de placas de veículos**, é altamente recomendável substituí-lo por um modelo YOLO treinado especificamente para essa tarefa. Você pode treinar o seu próprio modelo ou encontrar modelos pré-treinados na comunidade.