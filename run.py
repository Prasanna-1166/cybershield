"""
run.py
------
WHAT: The entry point used to start the Flask development server.
WHERE: project root.
HOW TO RUN (Windows, venv activated, .env configured, MySQL DB created):
    python run.py

This reads FLASK_CONFIG from the environment to decide which config class
to use (development / testing / production); defaults to "development".
"""

import os

from app import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "development"))

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
