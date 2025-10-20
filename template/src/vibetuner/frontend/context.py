from vibetuner.context import Context


class AppContext(Context):
    # Add typed state here

    model_config = {"arbitrary_types_allowed": True}


ctx = AppContext()
