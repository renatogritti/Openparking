# -*- coding: utf-8 -*-
"""
Módulo de Banco de Dados para o OpenParking.

Este módulo gerencia todas as interações com o banco de dados SQLite,
incluindo a criação da estrutura (tabelas) e a inserção de novos dados
de detecção de placas. Utiliza SQLAlchemy para abstração do banco.

Author: Renato Gritti   
Date: 21/11/2025
"""

from datetime import datetime, timedelta
from typing import Optional
import logging

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Engine,
    select,
)
from sqlalchemy.exc import SQLAlchemyError

from config import DATABASE_URL

# --- Configuração do Banco de Dados ---
try:
    engine: Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    metadata: MetaData = MetaData()
except ImportError:
    logging.error("Driver do banco de dados não encontrado. Por favor, instale-o.")
    engine = None
    metadata = None

# Definição da tabela 'detections'
if metadata is not None:
    detections: Table = Table(
        "detections",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("timestamp", DateTime, default=datetime.utcnow),
        Column("license_plate", String, nullable=False, index=True),
        Column("image_path", String, nullable=True),
    )


def create_db_and_tables() -> None:
    """Cria o banco de dados e as tabelas, se não existirem."""
    if engine and metadata:
        try:
            metadata.create_all(engine)
            logging.info("Banco de dados e tabelas verificados/criados com sucesso.")
        except SQLAlchemyError as e:
            logging.error(f"Erro ao criar tabelas do banco de dados: {e}")


def check_existing_plate(plate: str) -> bool:
    """
    Verifica se uma placa foi registrada no último minuto.
    """
    if not engine:
        return True  # Evita novas inserções se o DB não estiver disponível

    try:
        with engine.connect() as connection:
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            statement = (
                select(detections)
                .where(detections.c.license_plate == plate)
                .where(detections.c.timestamp >= one_minute_ago)
                .limit(1)
            )
            result = connection.execute(statement).first()
            return result is not None
    except SQLAlchemyError as e:
        logging.error(f"Erro ao verificar placa existente: {e}")
        return True


def add_detection(plate: str, image_path: Optional[str] = None) -> bool:
    """
    Adiciona uma nova detecção se ela não foi registrada no último minuto.
    """
    if not engine or check_existing_plate(plate):
        return False

    try:
        with engine.connect() as connection:
            statement = detections.insert().values(
                license_plate=plate, image_path=image_path
            )
            connection.execute(statement)
            connection.commit()
            return True
    except SQLAlchemyError as e:
        logging.error(f"Erro ao adicionar detecção: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Testando o módulo de banco de dados...")
    create_db_and_tables()

    test_plate = "TESTE123"
    logging.info(f"Adicionando placa de teste: {test_plate}")
    success = add_detection(test_plate)
    if success:
        logging.info("Placa de teste adicionada com sucesso.")
    else:
        logging.error("Falha ao adicionar a primeira placa de teste.")

    logging.info(f"Tentando adicionar a mesma placa novamente (deve ser bloqueado)...")
    success_duplicate = add_detection(test_plate)
    if not success_duplicate:
        logging.info("Detecção duplicada bloqueada com sucesso, como esperado.")
    else:
        logging.error("ERRO: Placa duplicada foi adicionada indevidamente.")
