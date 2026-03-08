"""
==============================================
  MINTO HOLIDAYS - Python Backend Server
==============================================
  Database:   MongoDB
  DB Name:    minto_holidays_db

  Collections:
    bookings        → Tour bookings
    hotel_bookings  → Hotel reservations
    flight_bookings → Flight tickets
    train_bookings  → Train tickets
    contacts        → Enquiries

  Admin Panel:  http://localhost:8000/admin/login.html
  Password:     Username: minto   Password: minto2025

  Run:  python server.py
==============================================
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import json, os
from datetime import datetime

# ── ADMIN CREDENTIALS (change these!) ──
ADMIN_USERNAME = "minto"
ADMIN_PASSWORD = "minto2025"

# ── MONGODB CONNECTION ──
try:
    from pymongo import MongoClient
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.server_info()
    db = client["minto_holidays_db"]
    print("✅  MongoDB connected  →  Database: minto_holidays_db")
except Exception as e:
    db = None
    print(f"⚠️   MongoDB not connected: {e}")
    print("    Website still works, but bookings won't save to DB.")
    print("    Install: pip install pymongo")
    print("    Start MongoDB, then restart server.\n")


class MintoServer(SimpleHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # Clean terminal

    def do_OPTIONS(self):
        self._cors(); self.end_headers()

    def _cors(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_POST(self):
        path   = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}
        body["created_at"] = datetime.now().isoformat()

        # ── Public booking endpoints ──
        routes = {
            "/api/book-tour":    ("bookings",        "Tour booking successful!"),
            "/api/book-hotel":   ("hotel_bookings",  "Hotel booking confirmed!"),
            "/api/book-flight":  ("flight_bookings", "Flight booking submitted!"),
            "/api/book-train":   ("train_bookings",  "Train ticket booked!"),
            "/api/contact":      ("contacts",        "Message received! We'll reply within 24 hours."),
        }

        if path in routes:
            col, msg = routes[path]
            bid = "N/A"
            if db is not None:
                try:
                    res = db[col].insert_one(body)
                    bid = str(res.inserted_id)
                    print(f"  💾  [{col}]  {body.get('name','?')}  {body.get('phone','?')}")
                except Exception as e:
                    print(f"  ❌  DB error: {e}")
            self._json({"success": True, "message": msg, "booking_id": bid})

        elif path == "/api/admin/login":
            u = body.get("username","")
            p = body.get("password","")
            if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                self._json({"success": True, "token": "minto_admin_ok"})
            else:
                self._json({"success": False, "message": "Wrong credentials"}, 401)
        else:
            self._json({"error": "Not found"}, 404)

    def do_GET(self):
        path = urlparse(self.path).path

        # ── Admin data API ──
        if path == "/api/admin/data":
            if db is not None:
                try:
                    def fetch(col):
                        docs = list(db[col].find({}, {"_id": 0}).sort("created_at", -1).limit(500))
                        return docs
                    data = {
                        "tours":    fetch("bookings"),
                        "hotels":   fetch("hotel_bookings"),
                        "flights":  fetch("flight_bookings"),
                        "trains":   fetch("train_bookings"),
                        "contacts": fetch("contacts"),
                    }
                    self._json(data)
                except Exception as e:
                    self._json({"error": str(e)}, 500)
            else:
                self._json({"tours":[],"hotels":[],"flights":[],"trains":[],"contacts":[]})
            return

        # ── Serve static files ──
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

    print("\n" + "="*50)
    print("  🌴  MINTO HOLIDAYS SERVER STARTED")
    print("="*50)
    print(f"  Website   →  http://localhost:{port}")
    print(f"  Admin     →  http://localhost:{port}/admin/login.html")
    print(f"  Username  :  {ADMIN_USERNAME}")
    print(f"  Password  :  {ADMIN_PASSWORD}")
    print(f"  Database  :  minto_holidays_db")
    print("="*50)
    print("  Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋  Server stopped.")
