# -*- coding: utf-8 -*-
"""
MailSender MVP — Simple bulk email tool
Run: python app.py
"""

import os
import re
import smtplib
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

# Column name aliases (case-insensitive)
EMAIL_COLUMNS = ["email", "e-posta", "eposta", "mail", "e_posta"]
NAME_COLUMNS  = ["name", "isim", "ad", "adsoyad", "fullname", "full name", "ad soyad", "firstname"]


def find_column(df_columns: list[str], candidates: list[str]) -> str | None:
    lower_map = {c.lower().strip(): c for c in df_columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(str(email).strip()))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Parse CSV or Excel file and return recipient list."""
    if "file" not in request.files:
        return jsonify({"error": "Dosya seçilmedi."}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file, dtype=str)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file, dtype=str)
        else:
            return jsonify({"error": "Sadece .csv, .xlsx veya .xls dosyaları desteklenir."}), 400
    except Exception as exc:
        return jsonify({"error": f"Dosya okunamadı: {exc}"}), 400

    # Clean up column names
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")

    email_col = find_column(list(df.columns), EMAIL_COLUMNS)
    name_col  = find_column(list(df.columns), NAME_COLUMNS)

    if email_col is None:
        return jsonify({
            "error": 'E-posta sütunu bulunamadı. Sütun adı "email" veya "mail" olmalı.'
        }), 400

    valid, invalid = [], []

    for _, row in df.iterrows():
        raw_email = str(row[email_col]).strip() if pd.notna(row[email_col]) else ""
        name      = str(row[name_col]).strip()   if (name_col and pd.notna(row[name_col])) else ""

        if not raw_email or raw_email.lower() == "nan":
            continue

        entry = {"name": name, "email": raw_email}
        if is_valid_email(raw_email):
            valid.append(entry)
        else:
            invalid.append(entry)

    return jsonify({"valid": valid, "invalid": invalid})


@app.route("/send", methods=["POST"])
def send():
    """Send email to each recipient via SMTP."""
    data       = request.get_json(force=True)
    subject    = (data.get("subject") or "").strip()
    body       = (data.get("body") or "").strip()
    recipients = data.get("recipients") or []

    if not subject:
        return jsonify({"error": "Konu boş bırakılamaz."}), 400
    if not body:
        return jsonify({"error": "Mesaj içeriği boş bırakılamaz."}), 400
    if not recipients:
        return jsonify({"error": "Alıcı listesi boş."}), 400

    # Read SMTP config from environment
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_user or not smtp_pass:
        return jsonify({
            "error": "SMTP ayarları eksik. .env dosyasında SMTP_USER ve SMTP_PASS değerlerini gir."
        }), 500

    # Open SMTP connection once, send all emails
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
    except Exception as exc:
        return jsonify({"error": f"SMTP bağlantısı kurulamadı: {exc}"}), 500

    results = {"success": [], "failed": []}

    for r in recipients:
        to_email = r.get("email", "")
        to_name  = r.get("name", "") or to_email

        # Personalize body with {name} or {isim}
        personalized = body.replace("{name}", to_name).replace("{isim}", to_name)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = smtp_from
        msg["To"]      = to_email
        msg.attach(MIMEText(personalized, "plain", "utf-8"))

        try:
            server.sendmail(smtp_from, to_email, msg.as_string())
            results["success"].append({"email": to_email, "name": to_name})
        except Exception as exc:
            results["failed"].append({"email": to_email, "name": to_name, "error": str(exc)})

    try:
        server.quit()
    except Exception:
        pass

    results["total"]         = len(recipients)
    results["success_count"] = len(results["success"])
    results["failed_count"]  = len(results["failed"])
    return jsonify(results)


if __name__ == "__main__":
    print("\n✅  MailSender başlatıldı → http://localhost:5000\n")
    app.run(debug=True, port=5000)
