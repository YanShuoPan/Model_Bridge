from typing import Dict, Any, List, Type

class BaseMethod:
    id: str = "base"
    name: str = "Base Method"
    requires: Dict[str, str] = {}  # e.g. {"y":"binary"}

    def run(self, df, roles: dict, params: dict, out_dir: str) -> Dict[str, Any]:
        raise NotImplementedError

# Registry
METHODS_REGISTRY: Dict[str, Type[BaseMethod]] = {}

def register(cls: Type[BaseMethod]):
    METHODS_REGISTRY[cls.id] = cls
    return cls
