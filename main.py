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
from typing import List, Optional

import cv2
import numpy as np

from src.camera import Camera
from src.database import add_detection, create_db_and_tables
from src.detector import Detector
from src.ocr_engine import OCREngine
import src.utils as utils

# Expressão Regular (Regex) para validar placas de veículos brasileiros.
# Formato Mercosul: LLLNLNN (ex: ABC4E67)
# Formato Antigo: LLLNNNN (ex: ABC1234)
PLATE_REGEX: str = r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}[0-9]{4}$"


def main() -> None:
    """
    Função principal que executa o pipeline de LPR.
    """
    print("Iniciando o OpenParking LPR...")

    # --- INICIALIZAÇÃO ---
    try:
        print("Inicializando o banco de dados...")
        create_db_and_tables()

        # Inicializa os componentes do pipeline.
        # Use 0 para webcam, ou forneça o caminho para um arquivo de vídeo.
        camera: Camera = Camera(source=0)
        detector: Detector = Detector(model_path="yolov8n.pt")
        ocr_engine: OCREngine = OCREngine()

    except Exception as e:
        print(f"[ERRO] Falha ao inicializar o pipeline: {e}")
        return

    print("Pipeline inicializado com sucesso. Iniciando processamento do vídeo...")

    # --- LOOP PRINCIPAL DE PROCESSAMENTO ---
    try:
        while True:
            ret: bool
            frame: Optional[np.ndarray]
            ret, frame = camera.get_frame()

            if not ret or frame is None:
                print("Fim do stream de vídeo ou erro na câmera.")
                break

            # 1. Detecção de Placas
            plate_bboxes: List[np.ndarray] = detector.detect_plates(frame)

            # Processa cada placa detectada
            for bbox in plate_bboxes:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 2. Pré-processamento da Placa
                plate_crop: np.ndarray = detector.crop_plate(frame, bbox)
                if plate_crop.size == 0:
                    continue

                filtered_plate: np.ndarray = utils.apply_image_filters(plate_crop)

                # 3. Inferência de OCR
                plate_text: Optional[str] = ocr_engine.recognize_plate(filtered_plate)

                if plate_text:
                    # 4. Validação
                    if re.match(PLATE_REGEX, plate_text):
                        print(f"PLACA VÁLIDA DETECTADA: {plate_text}")
                        # 5. Armazenamento
                        try:
                            add_detection(plate=plate_text)
                            print(f"Placa '{plate_text}' salva no banco de dados.")
                        except Exception as e:
                            print(f"[AVISO] Não foi possível salvar a placa no banco de dados: {e}")

                        # Desenha o texto reconhecido no quadro
                        cv2.putText(
                            frame, plate_text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2,
                        )
                    else:
                        print(f"Formato de placa inválido encontrado: {plate_text}")

            # Exibe o quadro resultante
            cv2.imshow("OpenParking LPR", frame)

            # Interrompe o loop se a tecla 'q' for pressionada
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Tecla 'q' pressionada, encerrando a aplicação.")
                break
    finally:
        # --- LIMPEZA DE RECURSOS ---
        print("Liberando recursos...")
        camera.release()
        cv2.destroyAllWindows()
        print("Aplicação finalizada.")


if __name__ == "__main__":
    main()