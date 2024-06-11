from youtubedlWeb import create_app, socketio

app = create_app()

def main():
    socketio.run(app)

if __name__ == "__main__":
    main()