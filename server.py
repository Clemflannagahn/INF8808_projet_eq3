"""
Contains the server to run our application.
"""
from flask_failsafe import failsafe
import sys
import os

@failsafe
def create_app():
    """
    Gets the underlying Flask server from our Dash app.

    Returns:
        The server to be run.
    """
    # the import is intentionally inside to work with the server failsafe
    from app import app  # pylint: disable=import-outside-toplevel
    return app.server

# Create the WSGI callable that Gunicorn expects.
server = create_app()

if __name__ == "__main__":
    # Version locale
    server.run(port="8050", debug=True)

    # Version serveur
    # port = int(os.environ.get("PORT", 8050))
    # Utilise 0.0.0.0 pour écouter sur toutes les interfaces.
    # server.run(port=port, debug=True, host='0.0.0.0')