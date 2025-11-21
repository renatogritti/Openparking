# -*- coding: utf-8 -*-
"""
Módulo da Câmera.

Este módulo fornece uma classe que encapsula a funcionalidade do
`cv2.VideoCapture` do OpenCV para gerenciar streams de vídeo de webcams
ou arquivos de forma mais simples e segura.

Author: Renato Gritti
Date: 21/11/2025
"""

from typing import Optional, Tuple, Union

import cv2
import numpy as np


class Camera:
    """
    Uma classe que encapsula `cv2.VideoCapture` para lidar com streams de vídeo.
    """

    def __init__(self, source: Union[int, str]) -> None:
        """
        Inicializa o stream da câmera.

        Args:
            source (Union[int, str]): A fonte da câmera. Pode ser um índice
                                      de dispositivo (ex: 0 para webcam padrão)
                                      ou o caminho para um arquivo de vídeo.

        Raises:
            IOError: Se a fonte de vídeo não puder ser aberta.
        """
        self.cap: cv2.VideoCapture = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise IOError(f"Não foi possível abrir a fonte de vídeo: {source}")
        self.source: Union[int, str] = source
        print(f"Câmera inicializada com a fonte: {self.source}")

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lê um único quadro (frame) do stream de vídeo.

        Returns:
            Tuple[bool, Optional[np.ndarray]]: Uma tupla contendo um booleano
                de sucesso e o quadro capturado (np.ndarray). Se a leitura
                falhar, retorna (False, None).
        """
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        return ret, frame

    def release(self) -> None:
        """
        Libera o recurso da câmera.
        """
        if self.cap.isOpened():
            self.cap.release()
            print(f"Fonte da câmera {self.source} liberada.")

    def __del__(self) -> None:
        """
        Destrutor para garantir que a câmera seja liberada quando o objeto
        for destruído.
        """
        self.release()


if __name__ == "__main__":
    print("Testando o módulo Camera...")
    # Este teste tentará acessar a webcam padrão (índice 0).
    # Pode falhar se não houver webcam ou se as permissões forem negadas.
    try:
        cam = Camera(0)
        ret, frame = cam.get_frame()
        if ret and frame is not None:
            print(f"Quadro capturado com sucesso. Shape: {frame.shape}")
        else:
            print("Falha ao capturar quadro da webcam.")
        cam.release()
    except IOError as e:
        print(f"Erro: {e}")
        print("Não foi possível executar o teste da câmera. Isso é esperado se nenhuma webcam estiver disponível.")