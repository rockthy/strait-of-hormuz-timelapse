import os
import sys
import smtplib
from email.message import EmailMessage

def send_email(recipient_email, video_url):
    """
    Sends an email notification using SMTP.
    Note: For GitHub Actions, you would typically use a dedicated Email Action 
    or configure secrets for an SMTP server (like SendGrid, Mailgun, or Gmail App Passwords).
    """
    subject = "Strait of Hormuz Daily Timelapse Video"
    content = f"Here is your daily time-lapse video of the Strait of Hormuz: {video_url}"
    
    print(f"Notification prepared for {recipient_email}")
    print(f"Subject: {subject}")
    print(f"Content: {content}")
    
    # Example SMTP configuration (requires secrets in GitHub Actions)
    # smtp_server = os.environ.get("SMTP_SERVER")
    # smtp_port = os.environ.get("SMTP_PORT")
    # smtp_user = os.environ.get("SMTP_USER")
    # smtp_pass = os.environ.get("SMTP_PASSWORD")
    
    # if all([smtp_server, smtp_port, smtp_user, smtp_pass]):
    #     msg = EmailMessage()
    #     msg.set_content(content)
    #     msg['Subject'] = subject
    #     msg['From'] = smtp_user
    #     msg['To'] = recipient_email
    #     
    #     with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
    #         server.login(smtp_user, smtp_pass)
    #         server.send_message(msg)
    #     print("Email sent via SMTP.")
    # else:
    #     print("SMTP credentials not found. Email not sent.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_email.py <recipient_email> <video_url>")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    video_url = sys.argv[2]
    send_email(recipient_email, video_url)
