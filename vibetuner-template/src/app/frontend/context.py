from vibetuner.context import Context as BaseContext


class Context(BaseContext):
    model_config = {"arbitrary_types_allowed": True}


ctx = Context()
