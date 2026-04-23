import os
import sys
import json
from manus_mcp_cli import tool_call

def send_email(recipient_email, video_url):
    subject = "Strait of Hormuz Daily Timelapse Video"
    content = f"Here is your daily time-lapse video of the Strait of Hormuz: {video_url}"
    
    messages = [
        {
            "to": [recipient_email],
            "subject": subject,
            "content": content
        }
    ]
    
    try:
        # Call the gmail_send_messages tool
        result = tool_call(
            tool_name="gmail_send_messages",
            server_name="gmail",
            input=json.dumps({"messages": messages})
        )
        print(f"Email sent successfully: {result}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_email.py <recipient_email> <video_url>")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    video_url = sys.argv[2]
    send_email(recipient_email, video_url)
