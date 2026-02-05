"""
Geçmiş Yöneticisi - Geri Al (Undo) / Yeniden Yap (Redo) işlevselliği.
Görüntü durumlarını bir yığın (stack) yapısında tutar.
Bellek verimliliği için maksimum durum sayısı sınırlandırılmıştır.
"""

import numpy as np
from typing import Optional

from app.utils.constants import MAX_HISTORY_STATES


class HistoryManager:
    """
    Geri alma/yeniden yapma yığınlarını yöneten sınıf.
    Her durum, görüntünün tam bir kopyasını içerir.
    FIFO mantığıyla en eski durumlar otomatik silinir.
    """

    def __init__(self, max_states: int = MAX_HISTORY_STATES):
        # Geri alma yığını (en son durum en sonda)
        self._undo_stack: list[np.ndarray] = []
        # Yeniden yapma yığını
        self._redo_stack: list[np.ndarray] = []
        # Maksimum tutulacak durum sayısı
        self._max_states = max_states

    def push_state(self, image: np.ndarray) -> None:
        """
        Yeni bir görüntü durumunu geçmişe ekler.
        Yeni durum eklendiğinde redo yığını temizlenir
        (yeni bir dallanma başladığı için).
        """
        if image is None:
            return

        # Görüntünün bağımsız kopyasını al
        self._undo_stack.append(image.copy())

        # Maksimum durum sayısını aşarsa en eskisini sil
        if len(self._undo_stack) > self._max_states:
            self._undo_stack.pop(0)

        # Yeni işlem yapıldığında redo geçersiz olur
        self._redo_stack.clear()

    def undo(self) -> Optional[np.ndarray]:
        """
        Son işlemi geri alır.
        Geri alınan durumu redo yığınına taşır.
        Döndürülen değer: Önceki görüntü durumu veya None.
        """
        if len(self._undo_stack) < 2:
            # En az 2 durum gerekli (mevcut + bir önceki)
            return None

        # Mevcut durumu redo yığınına taşı
        current = self._undo_stack.pop()
        self._redo_stack.append(current)

        # Bir önceki durumu döndür (yığında bırak)
        return self._undo_stack[-1].copy()

    def redo(self) -> Optional[np.ndarray]:
        """
        Geri alınan işlemi yeniden uygular.
        Döndürülen değer: Sonraki görüntü durumu veya None.
        """
        if not self._redo_stack:
            return None

        # Redo yığınından al ve undo yığınına ekle
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return state.copy()

    def can_undo(self) -> bool:
        """Geri alma yapılabilir mi kontrolü."""
        return len(self._undo_stack) >= 2

    def can_redo(self) -> bool:
        """Yeniden yapma yapılabilir mi kontrolü."""
        return len(self._redo_stack) > 0

    @property
    def undo_count(self) -> int:
        """Geri alınabilecek işlem sayısı."""
        return max(0, len(self._undo_stack) - 1)

    @property
    def redo_count(self) -> int:
        """Yeniden yapılabilecek işlem sayısı."""
        return len(self._redo_stack)

    def clear(self) -> None:
        """Tüm geçmişi temizler."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def get_current_state(self) -> Optional[np.ndarray]:
        """Mevcut (en son) durumun kopyasını döndürür."""
        if not self._undo_stack:
            return None
        return self._undo_stack[-1].copy()
