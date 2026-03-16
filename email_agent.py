import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to_address, subject, body):
    """Sends an email using the configured SMTP server."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not configured. Skipping email.")
        return

    try:
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = EMAIL_ADDRESS
        message['To'] = to_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # Use your SMTP server
        session.starttls()  # Enable security
        session.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login with mail_id and password
        text = message.as_string()
        session.sendmail(EMAIL_ADDRESS, to_address, text)
        session.quit()
        print(f"Mail Sent to {to_address}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_welcome_email(email, username):
    """Sends a welcome email to a new user."""
    subject = "Welcome to the PlantGuardian AI!"
    body = f"""
    Hi {username},

    Thank you for registering for the PlantGuardian AI! We're excited to have you.

    You can now analyze your plants, chat with our expert assistant, and explore our premium features. You have 20 free trials to get you started with our Gemini-powered analysis.

    Happy planting!

    Best,
    The PlantGuardian AI Team
    """
    send_email(email, subject, body)

def send_advertisement_email(email, package_name, price):
    """Sends an advertisement email to a user."""
    subject = f"Special Offer on our {package_name} Package!"
    body = f"""
    Hi there,

    Don't miss out on our exclusive offer for the {package_name} package, available for just {price}!

    Upgrade now to unlock advanced features and take your plant care to the next level.

    Best,
    The PlantGuardian AI Team
    """
    send_email(email, subject, body)