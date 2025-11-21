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

    def _post_process_plate_text(self, text: str) -> str:
        """
        Aplica regras de pós-processamento para corrigir erros comuns do OCR,
        considerando o formato das placas brasileiras.

        Args:
            text (str): O texto da placa bruto, após limpeza inicial.

        Returns:
            str: O texto da placa corrigido.
        """
        # Se o texto não tiver 7 caracteres, retorna como está, pois a lógica
        # posicional não se aplica.
        if not text or len(text) != 7:
            return text

        corrected_text = list(text)

        # Mapeamento para posições que DEVEM ser LETRAS (índices 0, 1, 2)
        # Converte um dígito lido erroneamente para uma letra parecida.
        letter_map = {"0": "O", "1": "I", "5": "S", "8": "B"}
        for i in range(3):
            if corrected_text[i] in letter_map:
                corrected_text[i] = letter_map[corrected_text[i]]

        # Mapeamento para posições que DEVEM ser NÚMEROS
        # Converte uma letra lida erroneamente para um número parecido.
        number_map = {"O": "0", "I": "1", "S": "5", "G": "6", "Z": "2", "B": "8", "A": "4"}

        # Verifica se a placa segue o padrão antigo (LLLNNNN) ou Mercosul (LLLNLNN)
        # pela natureza do 5º caractere (índice 4).
        is_mercosul: bool = corrected_text[4].isalpha()

        if is_mercosul:
            # Padrão LLLNLNN
            # Índice 3 (Número)
            if corrected_text[3] in number_map:
                corrected_text[3] = number_map[corrected_text[3]]
            # Índice 4 (Letra) - já verificada
            if corrected_text[4] in letter_map:
                 corrected_text[4] = letter_map[corrected_text[4]]
            # Índices 5, 6 (Números)
            for i in range(5, 7):
                if corrected_text[i] in number_map:
                    corrected_text[i] = number_map[corrected_text[i]]
        else:
            # Padrão LLLNNNN (ou erro de leitura)
            # Assume que os últimos 4 caracteres devem ser números
            for i in range(3, 7):
                if corrected_text[i] in number_map:
                    corrected_text[i] = number_map[corrected_text[i]]

        return "".join(corrected_text)

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

        # Pega os primeiros 7 caracteres, caso o OCR leia algo a mais.
        # Isso ajuda a focar na parte que mais provavelmente é a placa.
        base_text: str = cleaned_text[:7]

        # Aplica o pós-processamento para corrigir erros.
        corrected_text: str = self._post_process_plate_text(base_text)
        
        # Retorna o texto corrigido se ele tiver o comprimento esperado.
        if len(corrected_text) == 7:
            return corrected_text

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