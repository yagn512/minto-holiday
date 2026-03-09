"""
MINTO HOLIDAYS - Server (SQLite Database)
==========================================
Run:    python server.py
Site:   http://localhost:8000
Admin:  http://localhost:8000/login.html
Login:  minto / minto2025
==========================================
Database: minto_holidays.db  (auto-created in same folder)
No external dependencies — uses Python built-in sqlite3.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import json, os, sqlite3
from datetime import datetime

ADMIN_USERNAME = "minto"
ADMIN_PASSWORD = "minto2025"
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minto_holidays.db")

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT, email TEXT, phone TEXT,
            tour        TEXT, travel_date TEXT, persons TEXT,
            budget      TEXT, message TEXT, created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS hotel_bookings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT, email TEXT, phone TEXT,
            hotel_name  TEXT, city TEXT, check_in TEXT,
            check_out   TEXT, room_type TEXT, created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS flight_bookings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT, email TEXT, phone TEXT,
            from_city      TEXT, to_city TEXT, departure_date TEXT,
            class_type     TEXT, detail TEXT, created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS train_bookings (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT, email TEXT, phone TEXT,
            from_station TEXT, to_station TEXT, train_name TEXT,
            travel_date  TEXT, class_type TEXT, detail TEXT, created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT, email TEXT, phone TEXT,
            subject    TEXT, message TEXT, created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ SQLite database ready →", DB_FILE)


def rows_to_list(rows):
    return [dict(r) for r in rows]


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

    def do_POST(self):
        path   = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}
        now    = datetime.now().isoformat()

        conn = get_db()
        c    = conn.cursor()

        try:
            if path == "/api/book-tour":
                c.execute(
                    "INSERT INTO bookings (name,email,phone,tour,travel_date,persons,budget,message,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (body.get("name",""), body.get("email",""), body.get("phone",""),
                     body.get("tour",""), body.get("travel_date",""), body.get("persons",""),
                     body.get("budget",""), body.get("message",""), now)
                )
                conn.commit()
                bid = c.lastrowid
                print(f"  💾 [tour]    #{bid}  {body.get('name','?')}  {body.get('phone','?')}")
                self._json({"success": True, "message": "Tour booking successful!", "booking_id": bid})

            elif path == "/api/book-hotel":
                c.execute(
                    "INSERT INTO hotel_bookings (name,email,phone,hotel_name,city,check_in,check_out,room_type,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (body.get("name",""), body.get("email",""), body.get("phone",""),
                     body.get("hotel_name",""), body.get("city",""), body.get("check_in",""),
                     body.get("check_out",""), body.get("room_type",""), now)
                )
                conn.commit()
                bid = c.lastrowid
                print(f"  💾 [hotel]   #{bid}  {body.get('name','?')}  {body.get('phone','?')}")
                self._json({"success": True, "message": "Hotel booking confirmed!", "booking_id": bid})

            elif path == "/api/book-flight":
                c.execute(
                    "INSERT INTO flight_bookings (name,email,phone,from_city,to_city,departure_date,class_type,detail,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (body.get("name",""), body.get("email",""), body.get("phone",""),
                     body.get("from_city",""), body.get("to_city",""), body.get("departure_date",""),
                     body.get("class_type",""), body.get("detail",""), now)
                )
                conn.commit()
                bid = c.lastrowid
                print(f"  💾 [flight]  #{bid}  {body.get('name','?')}  {body.get('phone','?')}")
                self._json({"success": True, "message": "Flight booking submitted!", "booking_id": bid})

            elif path == "/api/book-train":
                c.execute(
                    "INSERT INTO train_bookings (name,email,phone,from_station,to_station,train_name,travel_date,class_type,detail,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (body.get("name",""), body.get("email",""), body.get("phone",""),
                     body.get("from_station",""), body.get("to_station",""), body.get("train_name",""),
                     body.get("travel_date",""), body.get("class_type",""), body.get("detail",""), now)
                )
                conn.commit()
                bid = c.lastrowid
                print(f"  💾 [train]   #{bid}  {body.get('name','?')}  {body.get('phone','?')}")
                self._json({"success": True, "message": "Train ticket booked!", "booking_id": bid})

            elif path == "/api/contact":
                c.execute(
                    "INSERT INTO contacts (name,email,phone,subject,message,created_at) VALUES (?,?,?,?,?,?)",
                    (body.get("name",""), body.get("email",""), body.get("phone",""),
                     body.get("subject",""), body.get("message",""), now)
                )
                conn.commit()
                bid = c.lastrowid
                print(f"  💾 [contact] #{bid}  {body.get('name','?')}  {body.get('email','?')}")
                self._json({"success": True, "message": "Message received!", "booking_id": bid})

            else:
                self._json({"error": "Not found"}, 404)

        except Exception as e:
            print(f"  ❌ DB error: {e}")
            self._json({"success": False, "error": str(e)}, 500)
        finally:
            conn.close()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/admin/data":
            conn = get_db()
            try:
                def fetch(table):
                    return rows_to_list(conn.execute(
                        f"SELECT * FROM {table} ORDER BY id DESC LIMIT 500"
                    ).fetchall())

                self._json({
                    "tours":    fetch("bookings"),
                    "hotels":   fetch("hotel_bookings"),
                    "flights":  fetch("flight_bookings"),
                    "trains":   fetch("train_bookings"),
                    "contacts": fetch("contacts"),
                })
            except Exception as e:
                self._json({"error": str(e)}, 500)
            finally:
                conn.close()
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
    init_db()
    port   = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), MintoServer)
    print(f"\n{'='*42}")
    print(f"  🌴  MINTO HOLIDAYS SERVER")
    print(f"{'='*42}")
    print(f"  Website → http://localhost:{port}")
    print(f"  Admin   → http://localhost:{port}/login.html")
    print(f"  Login   → minto  /  minto2025")
    print(f"  DB file → minto_holidays.db")
    print(f"{'='*42}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped.")
