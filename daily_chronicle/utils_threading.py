# daily_chronicle/utils_threading.py
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

class WorkerSignals(QObject):
    finished = Signal(object)

class WorkerRunnable(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        result = self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit(result)
