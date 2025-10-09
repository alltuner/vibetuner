from beanie import Document, View

from .core import CORE_MODELS


APP_MODELS: list[type[Document] | type[View]] = [
    # App Specific Models
]

# Custom Logic such as model rebuilds or migrations can be added here

MODELS = CORE_MODELS + APP_MODELS
