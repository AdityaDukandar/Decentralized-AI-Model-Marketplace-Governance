from abc import ABC, abstractmethod
from typing import Dict, Any

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, model_path: str) -> Dict[str, Any]:
        pass

class GovernancePolicy(ABC):
    @abstractmethod
    def can_access(self, user: Dict[str, Any], model_meta: Dict[str, Any]) -> bool:
        pass

class PricingStrategy(ABC):
    @abstractmethod
    def price(self, model_meta: Dict[str, Any]) -> float:
        pass

class StorageService(ABC):
    @abstractmethod
    def save(self, model_id: str, content: bytes) -> str:
        pass
