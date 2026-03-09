"""
MINTO HOLIDAYS - Server (MongoDB)
==========================================
Run:    python server.py
Site:   http://localhost:8000
Admin:  http://localhost:8000/login.html
Login:  minto / minto2025
==========================================

MongoDB setup:
  Local:  MONGO_URI = "mongodb://localhost:27017/"   (default)
  Atlas:  MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"

  Set via environment variable:
    Windows:  set MONGO_URI=mongodb+srv://...
    Linux/Mac: export MONGO_URI=mongodb+srv://...

Fallback: Agar MongoDB connect nahi hua toh data
          backup_data.json file mein save hota rahega.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import json, os
from datetime import datetime

ADMIN_USERNAME = "minto"
ADMIN_PASSWORD = "minto2025"
BACKUP_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_data.json")

# ─── MONGODB SETUP ────────────────────────────────────────────────────────────

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

db = None
try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
    client.server_info()   # force connection check
    db = client["minto_holidays_db"]
    print(f"✅ MongoDB connected!  ({MONGO_URI.split('@')[-1]})")
except ImportError:
    print("⚠️  pymongo not installed. Run:  pip install pymongo")
    print("   Falling back to JSON backup file.")
except Exception as e:
    print(f"⚠️  MongoDB connect failed: {e}")
    print(f"   URI tried: {MONGO_URI}")
    print("   Falling back to JSON backup file.")

# ─── JSON FALLBACK HELPERS ───────────────────────────────────────────────────

def _load_backup():
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bookings": [], "hotel_bookings": [], "flight_bookings": [],
            "train_bookings": [], "contacts": []}

def _save_backup(data):
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def fallback_insert(collection, doc):
    """Save doc to JSON backup file when MongoDB is unavailable."""
    data = _load_backup()
    if collection not in data:
        data[collection] = []
    doc["_id"] = f"backup_{len(data[collection])+1}_{datetime.now().strftime('%H%M%S')}"
    data[collection].append(doc)
    _save_backup(data)
    return doc["_id"]

def fallback_all():
    """Read all data from JSON backup."""
    return _load_backup()

# ─── HTTP SERVER ──────────────────────────────────────────────────────────────

class MintoServer(SimpleHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── POST ──────────────────────────────────────────────────────────────────
    def do_POST(self):
        path   = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}
        body["created_at"] = datetime.now().isoformat()

        routes = {
            "/api/book-tour":   ("bookings",        "Tour booking successful!"),
            "/api/book-hotel":  ("hotel_bookings",  "Hotel booking confirmed!"),
            "/api/book-flight": ("flight_bookings", "Flight booking submitted!"),
            "/api/book-train":  ("train_bookings",  "Train ticket booked!"),
            "/api/contact":     ("contacts",        "Message received!"),
        }

        if path not in routes:
            self._json({"error": "Not found"}, 404)
            return

        col, msg = routes[path]
        bid = "N/A"

        if db is not None:
            # ── MongoDB ──
            try:
                res = db[col].insert_one(body)
                bid = str(res.inserted_id)
                print(f"  💾 [mongo/{col}] #{bid[:8]}  {body.get('name','?')}  {body.get('phone','?')}")
            except Exception as e:
                print(f"  ❌ MongoDB insert error: {e}")
                # Even if mongo write fails mid-run, save to backup
                bid = fallback_insert(col, body)
                print(f"  💾 [backup/{col}] saved as fallback  id={bid}")
        else:
            # ── JSON fallback ──
            bid = fallback_insert(col, body)
            print(f"  💾 [backup/{col}] {body.get('name','?')}  {body.get('phone','?')}")

        self._json({"success": True, "message": msg, "booking_id": str(bid)})

    # ── GET ───────────────────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/admin/data":
            if db is not None:
                try:
                    def fetch(col):
                        docs = list(db[col].find({}, {"_id": 0}).sort("created_at", -1).limit(500))
                        return docs
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
                # Serve from JSON backup
                bk = fallback_all()
                # Sort each list by created_at descending
                for key in bk:
                    bk[key] = sorted(bk[key], key=lambda x: x.get("created_at",""), reverse=True)
                self._json({
                    "tours":    bk.get("bookings", []),
                    "hotels":   bk.get("hotel_bookings", []),
                    "flights":  bk.get("flight_bookings", []),
                    "trains":   bk.get("train_bookings", []),
                    "contacts": bk.get("contacts", []),
                })
            return

        if path == "/" or path == "":
            self.path = "/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def _json(self, data, code=200):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port   = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), MintoServer)

    mode = "MongoDB" if db is not None else "JSON Backup (MongoDB offline)"

    print(f"\n{'='*44}")
    print(f"  🌴  MINTO HOLIDAYS SERVER")
    print(f"{'='*44}")
    print(f"  Website  → http://localhost:{port}")
    print(f"  Admin    → http://localhost:{port}/login.html")
    print(f"  Login    → minto  /  minto2025")
    print(f"  Storage  → {mode}")
    if db is None:
        print(f"  Backup   → backup_data.json")
    print(f"{'='*44}")
    print(f"\n  To use MongoDB Atlas, set env variable:")
    print(f"  Windows:   set MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/")
    print(f"  Linux/Mac: export MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/")
    print(f"\n  To install pymongo:  pip install pymongo\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped.")
