# -*- coding: utf-8 -*-
"""
Dashboard Web com Flask para o OpenParking LPR.

Este script cria uma interface web para visualizar os dados de
reconhecimento de placas que foram armazenados no banco de dados pelo
script `main.py`.

Author: Renato Gritti
Date: 25/11/2025
"""

import pandas as pd
from flask import Flask, render_template
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import OperationalError
import logging

from config import DATABASE_URL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO)

# --- Configuração do Aplicativo Flask ---
app = Flask(__name__)

# --- Conexão com o Banco de Dados ---
try:
    engine: Engine = create_engine(DATABASE_URL)
except ImportError:
    logging.error("Driver do banco de dados não encontrado. Por favor, instale-o.")
    engine = None


def get_detections() -> pd.DataFrame:
    """
    Busca todas as detecções de placas do banco de dados.

    Returns:
        pd.DataFrame: Um DataFrame do Pandas com os dados das detecções.
                      Retorna um DataFrame vazio em caso de erro.
    """
    if not engine:
        return pd.DataFrame(columns=['timestamp', 'license_plate'])

    try:
        with engine.connect() as connection:
            query = text("SELECT timestamp, license_plate FROM detections ORDER BY timestamp DESC")
            df: pd.DataFrame = pd.read_sql(query, connection)
            # Formata a coluna de data/hora para melhor legibilidade
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            return df
    except OperationalError as e:
        logging.error(f"Erro ao conectar ou consultar o banco de dados: {e}")
        # Retorna um DataFrame vazio se a tabela não existir ou ocorrer um erro.
        return pd.DataFrame(columns=['timestamp', 'license_plate'])
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        return pd.DataFrame(columns=['timestamp', 'license_plate'])


# --- Rotas da Aplicação ---
@app.route('/')
def dashboard():
    """
    Renderiza o dashboard principal com os dados de detecção.
    """
    detections_df = get_detections()

    total_detections = len(detections_df)
    last_detection_time = "N/A"
    if not detections_df.empty:
        last_detection_time = detections_df['timestamp'].iloc[0]

    # Converte o DataFrame para uma lista de dicionários para o template
    detections_list = detections_df.to_dict(orient='records')

    return render_template(
        'index.html',
        total_detections=total_detections,
        last_detection_time=last_detection_time,
        detections=detections_list
    )


# --- Ponto de Entrada ---
if __name__ == '__main__':
    # Executa o aplicativo Flask em modo de depuração.
    # O modo de depuração permite o recarregamento automático após alterações no código.
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
