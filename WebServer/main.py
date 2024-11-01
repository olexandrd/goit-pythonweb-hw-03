import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)


class Template:
    def __init__(self, template, data):
        self.template = template
        self.data = data

    def refresh_data(self, data):
        self.data = data

    def render(self):
        env = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template(self.template)
        logging.info("Render template %s", self.template)
        return template.render(data=self.data)


class Storage:
    def __init__(self, file="./storage/data.json"):
        self.data = {}
        self.file = file

    def generate_key(self):
        return str(datetime.now())

    def add_data(self, value):
        key = self.generate_key()
        self.data[key] = value
        self.save_data()

    def save_data(self):
        with open(self.file, "w", encoding="utf-8") as fd:
            fd.write(json.dumps(self.data, indent=4))

    def get_data(self):
        return self.data

    def load_data(self):
        try:
            with open(self.file, "r", encoding="utf-8") as fd:
                self.data = json.loads(fd.read())
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.save_data()


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.storage = Storage()
        self.template = Template("info.html.jinja", self.storage.get_data())
        self.storage.load_data()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.storage.add_data(data_dict)
        self.storage.save_data()
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/read":
            self.template.refresh_data(self.storage.get_data())
            self.render_template()
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def render_template(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.template.render().encode())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        logging.info("Server started")
        logging.info("Listening on %s", server_address)
        logging.info("Press Ctrl+C to stop")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
