# -*- coding: utf-8 -*-
"""
Módulo de Banco de Dados para o OpenParking.

Este módulo gerencia todas as interações com o banco de dados SQLite,
incluindo a criação da estrutura (tabelas) e a inserção de novos dados
de detecção de placas. Utiliza SQLAlchemy para abstração do banco.

Author: Renato Gritti   
Date: 21/11/2025
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Engine,
)

# URL de conexão para o banco de dados SQLite.
# O banco será um arquivo na pasta 'data'.
DATABASE_URL: str = "sqlite:///./data/openparking.db"

# Engine do SQLAlchemy para conexão.
# `check_same_thread` é necessário para SQLite em ambientes multi-thread.
engine: Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata: MetaData = MetaData()

# Definição da tabela 'detections' para armazenar as placas reconhecidas.
detections: Table = Table(
    "detections",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow),
    Column("license_plate", String, nullable=False),
    Column("image_path", String, nullable=True),
)


def create_db_and_tables() -> None:
    """
    Cria o arquivo de banco de dados e as tabelas necessárias, caso não existam.
    """
    metadata.create_all(engine)


def add_detection(plate: str, image_path: Optional[str] = None) -> None:
    """
    Adiciona uma nova detecção de placa ao banco de dados.

    Args:
        plate (str): O texto da placa detectada.
        image_path (Optional[str], optional): O caminho para a imagem salva
                                              do carro/placa. Defaults to None.
    """
    with engine.connect() as connection:
        statement = detections.insert().values(
            license_plate=plate, image_path=image_path
        )
        connection.execute(statement)
        connection.commit()


if __name__ == "__main__":
    print("Inicializando banco de dados para teste...")
    create_db_and_tables()
    print("Banco de dados e tabelas criados com sucesso.")
    print("Adicionando uma detecção de teste...")
    add_detection("ABC-1234", "data/test_image.jpg")
    print("Detecção de teste adicionada.")