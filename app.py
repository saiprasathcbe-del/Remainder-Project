import os
import smtplib
import logging

from datetime import datetime
from zoneinfo import ZoneInfo
from email.message import EmailMessage

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# Load Gmail credentials
load_dotenv()

app = Flask(__name__)

# Timezone: India
TIMEZONE = ZoneInfo("Asia/Kolkata")

# Configure scheduler
scheduler = BackgroundScheduler(timezone=TIMEZONE)
scheduler.start()

logging.basicConfig(level=logging.INFO)


# --------------------------------
# GMAIL EMAIL SENDING FUNCTION
# --------------------------------

def send_email(receiver, message):

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        logging.error("Gmail credentials are missing.")
        return

    try:
        email = EmailMessage()

        email["Subject"] = "Smart Email Reminder"
        email["From"] = sender
        email["To"] = receiver

        email.set_content(
            "Hello!\n\n"
            "This is your scheduled reminder.\n\n"
            + message
            + "\n\nRegards,\nSmart Email Reminder"
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()
            server.login(sender, password)
            server.send_message(email)

        logging.info("Reminder email sent successfully.")

    except Exception:
        logging.exception("Email sending failed.")


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------
# SCHEDULE REMINDER
# --------------------------------

@app.route("/schedule", methods=["POST"])
def schedule():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    message = data.get("message", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()

    # Validate inputs
    if not all([email, message, date, time]):

        return jsonify({
            "message": "Please fill all fields!"
        }), 400

    # Check Gmail credentials
    if not os.getenv("EMAIL_ADDRESS") or not os.getenv("EMAIL_PASSWORD"):

        return jsonify({
            "message": "Gmail configuration is missing!"
        }), 500

    try:

        reminder_time = datetime.strptime(
            date + " " + time,
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=TIMEZONE)

    except ValueError:

        return jsonify({
            "message": "Invalid date or time!"
        }), 400

    # Check future date and time
    if reminder_time <= datetime.now(TIMEZONE):

        return jsonify({
            "message": "Please select a future date and time!"
        }), 400

    try:

        # Schedule automatic email
        job = scheduler.add_job(
            send_email,
            trigger="date",
            run_date=reminder_time,
            args=[email, message]
        )

        logging.info("Reminder scheduled: %s", reminder_time)

        return jsonify({
            "message": "Reminder scheduled successfully!",
            "job_id": job.id
        }), 200

    except Exception:

        logging.exception("Scheduling failed.")

        return jsonify({
            "message": "Unable to schedule reminder."
        }), 500


# --------------------------------
# RUN APPLICATION
# --------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False
    )