from app.src import app
from jahan.server import WSGIServer

application = app.application

if __name__ == '__main__':
    print("Serving on http://127.0.0.1:8000/ ")
    print('Press CTRL + C to exit..')
    server = WSGIServer('localhost', 8000, application)
    server.serve_forever()


# if __name__ == "__main__":
#     app.run()
