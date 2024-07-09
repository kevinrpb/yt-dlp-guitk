from abc import ABC, abstractmethod


class SimpleWidget(ABC):
    def __init__(self):
        self._create_layout()

    def __enter__(self):
        self._create_layout()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @abstractmethod
    def _create_layout(self):
        pass
