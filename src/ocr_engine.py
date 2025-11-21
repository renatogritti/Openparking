# -*- coding: utf-8 -*-
"""
Módulo do Motor de OCR (Reconhecimento Óptico de Caracteres).

Este módulo encapsula a biblioteca EasyOCR, fornecendo uma interface
simples para realizar o reconhecimento de texto em imagens de placas de veículos.

Author: Renato Gritti
Date: 21/11/2025
"""

import re
from typing import List, Optional

import easyocr
import numpy as np


class OCREngine:
    """
    Classe que encapsula o motor EasyOCR para reconhecimento de texto em placas.
    """

    def __init__(self, languages: Optional[List[str]] = None) -> None:
        """
        Inicializa o leitor EasyOCR.

        Na primeira execução, o EasyOCR fará o download dos modelos de linguagem
        necessários, o que pode levar algum tempo.

        Args:
            languages (Optional[List[str]], optional): Lista de códigos de
                linguagem a serem usados pelo OCR.
                Default é ['en', 'pt'].
        """
        if languages is None:
            languages = ["en", "pt"]
        self.reader: easyocr.Reader = easyocr.Reader(languages, gpu=False) # gpu=False para maior compatibilidade
        print("Motor EasyOCR inicializado.")

    def recognize_plate(self, plate_image: np.ndarray) -> Optional[str]:
        """
        Executa o OCR em uma imagem de placa recortada e processada.

        Args:
            plate_image (np.ndarray): A imagem da placa.

        Returns:
            Optional[str]: O texto da placa reconhecido, limpo e formatado,
                           ou None se nenhum texto for encontrado.
        """
        if plate_image is None or plate_image.size == 0:
            return None

        # O parâmetro `detail=0` retorna apenas o texto reconhecido.
        # `paragraph=False` trata linhas separadas como blocos de texto independentes.
        result: List[str] = self.reader.readtext(
            plate_image, detail=0, paragraph=False
        )

        if not result:
            return None

        # Combina os resultados e os limpa.
        raw_text: str = "".join(result).upper()
        # Remove caracteres inválidos (não alfanuméricos) e espaços.
        cleaned_text: str = re.sub(r"[^A-Z0-9]", "", raw_text)

        # Lógica simples: retorna a string mais longa que parece válida.
        # Isso pode ser melhorado com uma validação mais sofisticada.
        if len(cleaned_text) > 4:  # Verificação básica do comprimento da placa
            return cleaned_text

        return None


if __name__ == "__main__":
    # Este é um teste básico. Para um teste real, seria necessária uma
    # imagem de placa.
    print("Testando o OCREngine...")
    
    # Cria uma imagem preta para simular uma imagem de placa.
    mock_image: np.ndarray = np.zeros((60, 200, 3), dtype=np.uint8)
    mock_image.fill(200)  # Preenche com cinza

    try:
        engine = OCREngine()
        plate_text = engine.recognize_plate(mock_image)

        if plate_text:
            print(f"Resultado do reconhecimento no teste: {plate_text}")
        else:
            print("O reconhecimento falhou como esperado em uma imagem vazia.")
            
    except Exception as e:
        print(f"Não foi possível executar o teste do OCREngine: {e}")
        print("Isso pode ocorrer se os modelos do EasyOCR não puderam ser baixados.")