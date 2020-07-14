"""
    This file mainly serves as an entry point for the application and should
    not contain anything else than the main idiom provided below.
"""
from api import socketio, app


if __name__ == "__main__":
    socketio.run(app)
