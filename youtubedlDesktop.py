import webview
from youtubedlWeb import create_app, socketio

app = create_app()

def start_flask():
    socketio.run(app)

if __name__ == '__main__':
    import threading
    # Uruchom Flask w osobnym wątku
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Uruchom okno PyWebView
    app.window = webview.create_window('PyWebView z Flask', 'http://127.0.0.1:5000')
    app.desktop = True
    webview.start()