# -*- coding: utf-8 -*-
"""
Módulo do Detector de Objetos.

Este módulo encapsula o modelo de detecção de objetos YOLO (ultralytics)
para encontrar placas de veículos em um quadro de vídeo.

Author: Renato Gritti
Date: 21/11/2025
"""

from typing import List
import logging

import numpy as np
from ultralytics import YOLO

from config import DETECTION_THRESHOLD, MODEL_PATH


class Detector:
    """
    Classe que encapsula o modelo de detecção de objetos YOLO para encontrar placas.
    """

    def __init__(self, model_path: str = MODEL_PATH) -> None:
        """
        Inicializa o detector YOLO.

        Args:
            model_path (str): Caminho para o arquivo de pesos do modelo YOLO (.pt).
        """
        self.model: YOLO = YOLO(model_path)
        logging.info(f"Detector de objetos inicializado com o modelo: {model_path}")

    def detect_plates(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        Detecta placas de veículos em um determinado quadro de imagem.

        Args:
            frame (np.ndarray): O quadro de imagem da câmera.

        Returns:
            List[np.ndarray]: Uma lista de caixas delimitadoras para as placas detectadas.
        """
        if frame is None or frame.size == 0:
            return []

        results = self.model(frame, verbose=False)

        bboxes: List[np.ndarray] = []
        for result in results:
            for box in result.boxes:
                if box.cls == 0 and box.conf >= DETECTION_THRESHOLD:
                    xyxy: np.ndarray = box.xyxy.cpu().numpy().astype(int)[0]
                    bboxes.append(xyxy)

        return bboxes

    def crop_plate(self, frame: np.ndarray, bbox: np.ndarray) -> np.ndarray:
        """
        Recorta a placa do quadro original usando a caixa delimitadora.

        Args:
            frame (np.ndarray): O quadro de imagem original.
            bbox (np.ndarray): A caixa delimitadora no formato [x1, y1, x2, y2].

        Returns:
            np.ndarray: A imagem recortada da placa.
        """
        x1, y1, x2, y2 = bbox
        y1_buffered: int = max(0, y1 - 5)
        y2_buffered: int = min(frame.shape[0], y2 + 5)
        x1_buffered: int = max(0, x1 - 5)
        x2_buffered: int = min(frame.shape[1], x2 + 5)
        
        return frame[y1_buffered:y2_buffered, x1_buffered:x2_buffered]


if __name__ == "__main__":
    logging.info("Testando o Detector...")
    
    mock_image: np.ndarray = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_image.fill(128)

    try:
        detector = Detector()
        detected_boxes = detector.detect_plates(mock_image)

        if detected_boxes:
            logging.info(f"Encontrados {len(detected_boxes)} objetos em potencial.")
            first_plate_img = detector.crop_plate(mock_image, detected_boxes[0])
            logging.info(f"Primeiro objeto recortado com shape: {first_plate_img.shape}")
        else:
            logging.info("Nenhum objeto detectado na imagem de teste, como esperado.")

    except Exception as e:
        logging.error(f"Não foi possível executar o teste do Detector: {e}")