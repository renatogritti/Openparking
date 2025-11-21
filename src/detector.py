# -*- coding: utf-8 -*-
"""
Módulo do Detector de Objetos.

Este módulo encapsula o modelo de detecção de objetos YOLO (ultralytics)
para encontrar placas de veículos em um quadro de vídeo.

Author: Renato Gritti
Date: 21/11/2025
"""

from typing import List

import cv2
import numpy as np
from ultralytics import YOLO


class Detector:
    """
    Classe que encapsula o modelo de detecção de objetos YOLO para encontrar placas.
    """

    def __init__(self, model_path: str = "yolov8n.pt") -> None:
        """
        Inicializa o detector YOLO.

        Na primeira execução, a biblioteca `ultralytics` fará o download do
        modelo especificado se ele não for encontrado localmente.

        Args:
            model_path (str): Caminho para o arquivo de pesos do modelo YOLO (.pt).
                              O padrão é 'yolov8n.pt', um modelo genérico.
                              Para melhores resultados, use um modelo treinado
                              especificamente em placas de veículos.
        """
        self.model: YOLO = YOLO(model_path)
        print(f"Detector de objetos inicializado com o modelo: {model_path}")

    def detect_plates(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        Detecta placas de veículos em um determinado quadro de imagem.

        Args:
            frame (np.ndarray): O quadro de imagem da câmera.

        Returns:
            List[np.ndarray]: Uma lista de caixas delimitadoras (bounding boxes)
                              para as placas detectadas. Cada caixa está no
                              formato [x1, y1, x2, y2]. Retorna uma lista vazia
                              se nenhuma placa for encontrada.
        """
        if frame is None or frame.size == 0:
            return []

        # Realiza a inferência.
        # verbose=False para suprimir a saída de log do YOLO.
        results = self.model(frame, verbose=False)

        bboxes: List[np.ndarray] = []
        for result in results:
            for box in result.boxes:
                # NOTA: Um modelo genérico como 'yolov8n.pt' não possui uma classe
                # 'license_plate'. Este código assume que QUALQUER detecção é
                # uma placa em potencial. Em um cenário real, é OBRIGATÓRIO
                # filtrar pelo índice de classe correto.
                # Exemplo: `if box.cls == 0:` onde 0 é o ID da classe da placa.
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
        # Adiciona uma pequena margem para garantir que a placa inteira seja capturada.
        y1_buffered: int = max(0, y1 - 5)
        y2_buffered: int = min(frame.shape[0], y2 + 5)
        x1_buffered: int = max(0, x1 - 5)
        x2_buffered: int = min(frame.shape[1], x2 + 5)
        
        return frame[y1_buffered:y2_buffered, x1_buffered:x2_buffered]


if __name__ == "__main__":
    print("Testando o Detector...")
    
    # Cria uma imagem cinza para simular um quadro de vídeo.
    mock_image: np.ndarray = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_image.fill(128)

    try:
        # Isso fará o download do yolov8n.pt na primeira execução, se não existir.
        detector = Detector()
        detected_boxes = detector.detect_plates(mock_image)

        if detected_boxes:
            print(f"Encontrados {len(detected_boxes)} objetos em potencial.")
            # Recorta o primeiro objeto detectado
            first_plate_img = detector.crop_plate(mock_image, detected_boxes[0])
            print(f"Primeiro objeto recortado com shape: {first_plate_img.shape}")
        else:
            print("Nenhum objeto detectado na imagem de teste, como esperado.")

    except Exception as e:
        print(f"Não foi possível executar o teste do Detector: {e}")