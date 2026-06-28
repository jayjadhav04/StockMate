import os
from fastapi.templating import Jinja2Templates

# Base templates directory path relative to the app structure
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)
