# -*- coding: utf-8 -*-
"""
Ponto de Entrada Principal (Headless) para o OpenParking LPR.

Este script executa o pipeline de Reconhecimento de Placas de Veículos (LPR)
em modo de linha de comando (sem interface gráfica principal, além da janela
de vídeo do OpenCV). Ele captura vídeo da câmera, detecta placas, realiza OCR,
valida o formato da placa e armazena os resultados no banco de dados.

Author: Renato Gritti
Date: 21/11/2025
"""

import re
import logging
from typing import List, Optional

import cv2
import numpy as np

from src.camera import Camera
from src.database import add_detection, create_db_and_tables
from src.detector import Detector
from src.ocr_engine import OCREngine
import src.utils as utils
from config import PLATE_REGEX, CAMERA_SOURCE, MODEL_PATH

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO)


def process_plate(plate_text: str, frame: np.ndarray, bbox: List[int]) -> None:
    """
    Valida, armazena e desenha a placa no frame.
    """
    x1, y1, _, _ = bbox
    if re.match(PLATE_REGEX, plate_text):
        logging.info(f"PLACA VÁLIDA DETECTADA: {plate_text}")
        try:
            if add_detection(plate=plate_text):
                logging.info(f"Placa '{plate_text}' salva no banco de dados.")
            else:
                logging.info(f"Placa '{plate_text}' já registrada recentemente.")
        except Exception as e:
            logging.warning(f"Não foi possível salvar a placa '{plate_text}': {e}")

        cv2.putText(
            frame, plate_text, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2,
        )
    else:
        logging.info(f"Formato de placa inválido encontrado: {plate_text}")


def process_frame(frame: np.ndarray, detector: Detector, ocr_engine: OCREngine) -> None:
    """
    Processa um único frame de vídeo para detectar e reconhecer placas.
    """
    plate_bboxes = detector.detect_plates(frame)

    for bbox in plate_bboxes:
        x1, y1, x2, y2 = bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        plate_crop = detector.crop_plate(frame, bbox)
        if plate_crop.size == 0:
            continue

        corners = utils.find_plate_corners(plate_crop)
        
        if corners is not None:
            x1_buffered = max(0, x1 - 5)
            y1_buffered = max(0, y1 - 5)
            corners[:, 0] += x1_buffered
            corners[:, 1] += y1_buffered
            processed_plate = utils.four_point_transform(frame, corners)
            if processed_plate.size > 0:
                cv2.imshow("Placa Retificada", processed_plate)
        else:
            processed_plate = plate_crop

        filtered_plate = utils.apply_image_filters(processed_plate)
        plate_text = ocr_engine.recognize_plate(filtered_plate)

        if plate_text:
            process_plate(plate_text, frame, bbox)


def main() -> None:
    """
    Função principal que executa o pipeline de LPR.
    """
    logging.info("Iniciando o OpenParking LPR...")

    try:
        logging.info("Inicializando o banco de dados...")
        create_db_and_tables()

        camera = Camera(source=CAMERA_SOURCE)
        detector = Detector(model_path=MODEL_PATH)
        ocr_engine = OCREngine()

    except Exception as e:
        logging.error(f"Falha ao inicializar o pipeline: {e}")
        return

    logging.info("Pipeline inicializado. Iniciando processamento do vídeo...")

    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret or frame is None:
                logging.info("Fim do stream de vídeo ou erro na câmera.")
                break

            process_frame(frame, detector, ocr_engine)
            cv2.imshow("OpenParking LPR", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                logging.info("Tecla 'q' pressionada, encerrando a aplicação.")
                break
    finally:
        logging.info("Liberando recursos...")
        camera.release()
        cv2.destroyAllWindows()
        logging.info("Aplicação finalizada.")


if __name__ == "__main__":
    main()