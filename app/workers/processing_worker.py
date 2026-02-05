"""
Arka Plan İşleme Worker'ı - UI'yı bloke etmeden görüntü işleme.
QThread tabanlı çalışarak ana thread'in donmasını önler.
Debounce mekanizması ile gereksiz işleme tekrarları engellenir.
"""

import numpy as np
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, QThread, QMutex, QWaitCondition


class ProcessingWorker(QObject):
    """
    Arka planda görüntü işleme yapan worker.
    Sinyal-slot mekanizması ile UI thread'e güvenli sonuç iletimi sağlar.

    Sinyaller:
        processing_started: İşleme başladığında tetiklenir
        processing_finished: İşleme tamamlandığında (sonuç ile) tetiklenir
        error_occurred: Hata durumunda tetiklenir
    """

    # Sinyaller (thread-safe iletişim için)
    processing_started = Signal()
    processing_finished = Signal(np.ndarray)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        self._processor = None      # ImageProcessor referansı
        self._should_stop = False    # Durma bayrağı
        self._has_task = False       # Bekleyen görev var mı
        self._running = True         # Worker çalışıyor mu

    def set_processor(self, processor) -> None:
        """ImageProcessor referansını ayarlar."""
        self._processor = processor

    @Slot()
    def process(self) -> None:
        """
        Worker'ın ana döngüsü. Thread başlatıldığında çalışır.
        Görev gelene kadar bekler, görev gelince işler.
        """
        while self._running:
            self._mutex.lock()
            # Görev yoksa bekle
            while not self._has_task and self._running:
                self._condition.wait(self._mutex)

            if not self._running:
                self._mutex.unlock()
                break

            self._has_task = False
            self._mutex.unlock()

            # Görüntü işleme
            if self._processor is not None:
                try:
                    self.processing_started.emit()
                    result = self._processor.process_preview()
                    if result is not None and not self._should_stop:
                        self.processing_finished.emit(result)
                except Exception as e:
                    self.error_occurred.emit(str(e))

    def request_processing(self) -> None:
        """
        Yeni bir işleme görevi talep eder.
        Önceki bekleyen görev varsa yerine yenisi geçer (debounce).
        """
        self._mutex.lock()
        self._has_task = True
        self._should_stop = False
        self._condition.wakeOne()
        self._mutex.unlock()

    def stop(self) -> None:
        """Worker'ı güvenli bir şekilde durdurur."""
        self._mutex.lock()
        self._running = False
        self._should_stop = True
        self._condition.wakeOne()
        self._mutex.unlock()


class ProcessingThread:
    """
    Worker ve QThread'i yöneten yüksek seviye sınıf.
    Worker'ın yaşam döngüsünü (başlatma, durdurma) kapsüller.
    """

    def __init__(self):
        self._thread = QThread()
        self._worker = ProcessingWorker()
        # Worker'ı ayrı thread'e taşı
        self._worker.moveToThread(self._thread)
        # Thread başladığında worker'ın process metodunu çalıştır
        self._thread.started.connect(self._worker.process)

    @property
    def worker(self) -> ProcessingWorker:
        return self._worker

    def start(self) -> None:
        """Thread'i başlatır."""
        if not self._thread.isRunning():
            self._thread.start()

    def stop(self) -> None:
        """Thread'i güvenli şekilde durdurur ve temizler."""
        self._worker.stop()
        self._thread.quit()
        self._thread.wait(3000)  # Maksimum 3 saniye bekle

    def request_processing(self) -> None:
        """İşleme talebi gönderir."""
        self._worker.request_processing()
