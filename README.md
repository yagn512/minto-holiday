# 🌴 MINTO HOLIDAYS – COMPLETE WEBSITE

## 🗄️ DATABASE INFO

**Database Software:** MongoDB  
**Database Name:** `minto_holidays_db`

| Collection       | What is saved             |
|-----------------|--------------------------|
| `bookings`       | Tour package bookings     |
| `hotel_bookings` | Hotel reservations        |
| `flight_bookings`| Flight ticket requests    |
| `train_bookings` | Train ticket bookings     |
| `contacts`       | Contact / enquiry messages|

---

## 🔐 ADMIN PANEL

**URL:** `http://localhost:8000/admin/login.html`  
**Username:** `minto`  
**Password:** `minto2025`

> To change password — open `server.py`, find lines:
> `ADMIN_USERNAME = "minto"`
> `ADMIN_PASSWORD = "minto2025"`
> Change to your own.

---

## 🚀 HOW TO RUN

### Step 1 – Install pymongo (one time only)
```
pip install pymongo
```

### Step 2 – Start MongoDB
Windows: Search "Services" → Start "MongoDB"  
Or in Command Prompt: `net start MongoDB`

### Step 3 – Start the server
```
python server.py
```

### Step 4 – Open browser
```
Website:  http://localhost:8000
Admin:    http://localhost:8000/admin/login.html
```

---

## 📁 FILES

```
minto_holidays/
├── index.html          ← Home page
├── hotels.html         ← Hotel booking
├── flights.html        ← Flight booking  
├── trains.html         ← Train tickets
├── book.html           ← Tour booking form
├── kashmir.html        ← Tour detail
├── uttarakhand.html
├── golden.html
├── thailand.html
├── bali.html
├── about.html
├── contact.html
├── server.py           ← Python + MongoDB backend
├── admin/
│   ├── login.html      ← Admin login
│   └── dashboard.html  ← Database dashboard
├── css/style.css
├── js/main.js
└── images/
```

---

## 🌐 FREE HOSTING (Render.com)

1. Upload to GitHub
2. Go to render.com → New Web Service
3. Connect GitHub repo
4. Build command: `pip install pymongo`
5. Start command: `python server.py`
6. Add environment variable: `MONGO_URI` = your MongoDB Atlas URL

### MongoDB Atlas (Free Cloud DB)
1. Go to mongodb.com/atlas
2. Create free account
3. Create cluster → Get connection string
4. Set as `MONGO_URI` in Render
