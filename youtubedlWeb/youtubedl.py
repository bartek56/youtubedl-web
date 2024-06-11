from youtubedlWeb import create_app, socketio

app = create_app()

# script for running from library
def main():
    socketio.run(app)

if __name__ == "__main__":
    main()