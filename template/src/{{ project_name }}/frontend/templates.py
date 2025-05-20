from fastapi.templating import Jinja2Templates
from fasthx import Jinja

from .. import TEMPLATES_DIR

jinja = Jinja(Jinja2Templates(directory=TEMPLATES_DIR))
