# -*- coding: utf-8 -*-
"""
Arquivo de Configuração para o OpenParking LPR.

Este arquivo centraliza todas as variáveis de configuração do projeto
para facilitar a manutenção e a customização.
"""

# --- Configurações do Banco de Dados ---
DATABASE_URL: str = "sqlite:///./data/openparking.db"

# --- Configurações do Modelo ---
# Caminho para o modelo de detecção de placas treinado.
MODEL_PATH: str = "lpr_model.pt"
# Limiar de confiança para a detecção de placas. Somente detecções com
# confiança acima deste valor serão consideradas.
DETECTION_THRESHOLD: float = 0.5

# --- Configurações da Câmera ---
# Fonte da câmera. Use 0 para a webcam padrão ou o caminho para um arquivo de vídeo.
CAMERA_SOURCE: int | str = 0

# --- Configurações de Validação ---
# Expressão Regular (Regex) para validar placas de veículos brasileiros.
# Formato Mercosul: LLLNLNN (ex: ABC4E67)
# Formato Antigo: LLLNNNN (ex: ABC1234)
PLATE_REGEX: str = r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}[0-9]{4}$"

# --- Configurações do Servidor Web (Flask) ---
FLASK_HOST: str = "0.0.0.0"
FLASK_PORT: int = 5001
FLASK_DEBUG: bool = True
