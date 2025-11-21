# -*- coding: utf-8 -*-
"""
Dashboard Web com Streamlit para o OpenParking LPR.

Este script cria uma interface web simples para visualizar os dados de
reconhecimento de placas que foram armazenados no banco de dados pelo
script `main.py`.

Author: Renato Gritti
Date: 21/11/2025
"""

import pandas as pd
import streamlit as st
from sqlalchemy import Engine, create_engine, text


# URL do banco de dados, conforme definido em `src/database.py`.
DATABASE_URL: str = "sqlite:///./data/openparking.db"
engine: Engine = create_engine(DATABASE_URL)


@st.cache_data(ttl=10) # Cache por 10 segundos para não sobrecarregar o DB
def get_detections() -> pd.DataFrame:
    """
    Busca todas as detecções de placas do banco de dados.

    A função usa um cache do Streamlit para evitar consultas repetidas
    ao banco de dados em um curto período de tempo.

    Returns:
        pd.DataFrame: Um DataFrame do Pandas com os dados das detecções.
                      Retorna um DataFrame vazio em caso de erro.
    """
    try:
        with engine.connect() as connection:
            query = text("SELECT id, timestamp, license_plate FROM detections ORDER BY timestamp DESC")
            df: pd.DataFrame = pd.read_sql(query, connection)
            # Formata a coluna de data/hora para melhor legibilidade
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            return df
    except Exception as e:
        # Se a tabela ainda não existir, por exemplo.
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()


# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard LPR")

# --- Título ---
st.title("🅿️ Dashboard OpenParking LPR")
st.markdown("Visualizador de placas de veículos detectadas.")

st.write("---")

# --- Painel de Destaques ---
col1, col2 = st.columns(2)

# --- Seção Principal de Dados ---
st.subheader("Últimas Detecções")

# Botão de atualização
if st.button("Atualizar Dados"):
    st.cache_data.clear() # Limpa o cache para forçar a releitura dos dados
    st.rerun()

detections_df: pd.DataFrame = get_detections()

# Preenche os destaques
col1.metric("Total de Detecções", len(detections_df))
last_detection_time = detections_df['timestamp'].iloc[0] if not detections_df.empty else "N/A"
col2.metric("Última Detecção", last_detection_time)


if not detections_df.empty:
    # Exibe a tabela de dados
    st.dataframe(
        detections_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "timestamp": st.column_config.TextColumn("Data e Hora"),
            "license_plate": st.column_config.TextColumn("Placa"),
        }
    )
else:
    st.info("Nenhuma placa foi detectada ainda. Execute `main.py` para iniciar o processo.")

st.write("---")

# --- Seção Sobre ---
with st.expander("Sobre esta Aplicação"):
    st.markdown(
        """
        Este dashboard exibe os dados coletados pelo sistema de Reconhecimento de Placas.
        
        - O script `main.py` é responsável por rodar o pipeline de LPR, que processa o vídeo,
          detecta as placas e as salva no banco de dados.
        - Este dashboard (`app.py`) lê o banco de dados e exibe os resultados aqui.
        """
    )