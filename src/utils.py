# -*- coding: utf-8 -*-
"""
Módulo de Utilitários de Imagem.

Este módulo contém funções auxiliares para processamento de imagem,
como redimensionamento, filtros e transformações de perspectiva, que são
usadas no pipeline de LPR para pré-processar as imagens antes do OCR.

Author: Renato Gritti
Date: 21/11/2025
"""

from typing import Optional

import cv2
import numpy as np


def resize_image(
    image: np.ndarray,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> np.ndarray:
    """
    Redimensiona uma imagem para uma largura ou altura específica mantendo a proporção.

    Args:
        image (np.ndarray): A imagem de entrada.
        width (Optional[int]): A largura alvo.
        height (Optional[int]): A altura alvo.

    Returns:
        np.ndarray: A imagem redimensionada.
    """
    if width is None and height is None:
        return image

    (h, w) = image.shape[:2]

    if width is None and height is not None:
        r: float = height / float(h)
        dim: tuple[int, int] = (int(w * r), height)
    elif width is not None:
        r: float = width / float(w)
        dim: tuple[int, int] = (width, int(h * r))
    else: # Should not happen given the first check, but for completeness
        return image

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """
    Executa uma transformação de perspectiva para obter uma visão "de cima" da placa.
    Isso é frequentemente chamado de "deskewing" (correção de inclinação).

    Args:
        image (np.ndarray): A imagem original contendo a placa.
        pts (np.ndarray): Uma lista de 4 pontos (x, y) especificando as
                          coordenadas do contorno da placa. A ordem deve ser:
                          topo-esquerda, topo-direita, baixo-direita, baixo-esquerda.

    Returns:
        np.ndarray: A imagem da placa retificada.
    """
    rect: np.ndarray = np.array(pts, dtype="float32")
    (tl, tr, br, bl) = rect

    # Calcula a largura da nova imagem
    widthA: float = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB: float = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth: int = max(int(widthA), int(widthB))

    # Calcula a altura da nova imagem
    heightA: float = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB: float = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight: int = max(int(heightA), int(heightB))

    # Define os pontos de destino para a visão "de cima"
    dst: np.ndarray = np.array(
        [
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1],
        ],
        dtype="float32",
    )

    # Calcula a matriz de transformação de perspectiva e a aplica
    M: np.ndarray = cv2.getPerspectiveTransform(rect, dst)
    warped: np.ndarray = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def apply_image_filters(image: np.ndarray) -> np.ndarray:
    """
    Aplica uma série de filtros na imagem da placa para melhorar a precisão do OCR.

    Args:
        image (np.ndarray): A imagem de entrada da placa.

    Returns:
        np.ndarray: A imagem filtrada em escala de cinza.
    """
    # Converte para escala de cinza
    gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplica equalização de histograma para melhorar o contraste
    equalized: np.ndarray = cv2.equalizeHist(gray)

    # Outros filtros podem ser adicionados aqui, por exemplo:
    # - Filtro bilateral para reduzir ruído e manter bordas nítidas
    #   filtered = cv2.bilateralFilter(equalized, 11, 17, 17)
    # - Binarização para criar uma imagem preto e branco
    #   _, thresh = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return equalized


if __name__ == "__main__":
    print("Testando as funções de utilitários...")
    
    mock_image: np.ndarray = np.zeros((200, 400, 3), dtype=np.uint8)
    mock_image.fill(100)

    # Teste de redimensionamento
    resized = resize_image(mock_image, width=200)
    print(f"Shape original: {mock_image.shape}, Shape redimensionado: {resized.shape}")
    assert resized.shape[1] == 200

    # Teste de filtros
    filtered = apply_image_filters(mock_image)
    print(f"Shape da imagem filtrada: {filtered.shape}, Dtype: {filtered.dtype}")
    assert len(filtered.shape) == 2  # Deve ser escala de cinza

    # Teste de transformação de perspectiva (teste de placeholder)
    # Em um cenário real, `pts` viria de um algoritmo de detecção de contornos.
    mock_pts: np.ndarray = np.array([[20, 30], [380, 35], [375, 180], [25, 175]])
    warped = four_point_transform(mock_image, mock_pts)
    print(f"Shape da imagem retificada: {warped.shape}")
    assert warped.shape[0] > 0 and warped.shape[1] > 0

    print("Testes das funções de utilitários concluídos.")