import web
from web import httpserver

# URL mapping
urls = ("/", "FirmwareHandler")
app = web.application(urls, globals())

# Request handler
class FirmwareHandler:
    def GET(self):
        try:
            with open("FIRMWARE.hex", "r") as f:
                return f.read()
        except FileNotFoundError:
            return web.notfound("FIRMWARE.hex not found.")

if __name__ == "__main__":
    # Set your desired IP and port here
    host = "0.0.0.0"  # Or "127.0.0.1" for localhost only
    port = 8080

    # Use web.httpserver to start on custom port
    httpserver.runsimple(app.wsgifunc(), (host, port))
