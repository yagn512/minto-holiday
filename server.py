"""
MINTO HOLIDAYS - Server
Run: python server.py
Website: http://localhost:8000
Admin: http://localhost:8000/login.html
Username: minto | Password: minto2025
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import json, os
from datetime import datetime

ADMIN_USERNAME = "minto"
ADMIN_PASSWORD = "minto2025"

try:
    from pymongo import MongoClient
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    client.server_info()
    db = client["minto_holidays_db"]
    print("✅ MongoDB connected!")
except Exception as e:
    db = None
    print(f"⚠️  MongoDB not connected: {e}")

class MintoServer(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        body["created_at"] = datetime.now().isoformat()

        routes = {
            "/api/book-tour":   ("bookings",        "Tour booking successful!"),
            "/api/book-hotel":  ("hotel_bookings",  "Hotel booking confirmed!"),
            "/api/book-flight": ("flight_bookings", "Flight booking submitted!"),
            "/api/book-train":  ("train_bookings",  "Train ticket booked!"),
            "/api/contact":     ("contacts",        "Message received!"),
        }

        if path in routes:
            col, msg = routes[path]
            bid = "N/A"
            if db is not None:
                try:
                    res = db[col].insert_one(body)
                    bid = str(res.inserted_id)
                    print(f"  💾 [{col}] {body.get('name','?')} {body.get('phone','?')}")
                except Exception as e:
                    print(f"  ❌ DB error: {e}")
            self._json({"success": True, "message": msg, "booking_id": bid})
        else:
            self._json({"error": "Not found"}, 404)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/admin/data":
            if db is not None:
                try:
                    def fetch(col):
                        return list(db[col].find({}, {"_id": 0}).sort("created_at", -1).limit(500))
                    self._json({
                        "tours":    fetch("bookings"),
                        "hotels":   fetch("hotel_bookings"),
                        "flights":  fetch("flight_bookings"),
                        "trains":   fetch("train_bookings"),
                        "contacts": fetch("contacts"),
                    })
                except Exception as e:
                    self._json({"error": str(e)}, 500)
            else:
                self._json({"tours":[],"hotels":[],"flights":[],"trains":[],"contacts":[]})
            return
        if path == "/" or path == "":
            self.path = "/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def _json(self, data, code=200):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), MintoServer)
    print(f"\n{'='*40}")
    print(f"  🌴 MINTO HOLIDAYS SERVER")
    print(f"{'='*40}")
    print(f"  Website → http://localhost:{port}")
    print(f"  Admin   → http://localhost:{port}/login.html")
    print(f"  User: minto | Pass: minto2025")
    print(f"{'='*40}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped.")
