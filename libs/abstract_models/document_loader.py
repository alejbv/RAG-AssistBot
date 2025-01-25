from abc import ABC,abstractmethod

class DocumentLoader(ABC):
    @abstractmethod
    def load_data(self) -> None:
        raise NotImplementedError
    