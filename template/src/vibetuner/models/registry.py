from beanie import Document, View


_MODEL_REGISTRY: list[type[Document] | type[View]] = []


def register_model(cls):
    """Decorator to register a model"""
    _MODEL_REGISTRY.append(cls)
    return cls


def get_all_models():
    """Get all registered models (call at startup)"""
    return _MODEL_REGISTRY
