from wsgiref.simple_server import make_server
from framework import WebFramework as MyFramework

app = MyFramework()

@app.route("/")
def home():
    return "Welcome Home"

@app.route("/about")
def about():
    return "About Page"

class Contact:
    def __call__(self):
        return "Contact Page"

app.routes["/contact"] = Contact()

if __name__ == "__main__":
    with make_server('', 8000, app) as server:
        print("Running on http://localhost:8000")
        server.serve_forever()
