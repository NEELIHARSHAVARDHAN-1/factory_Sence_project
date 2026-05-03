import os
from twilio.rest import Client

def send_whatsapp(message: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM")
    to_whatsapp = os.getenv("TWILIO_WHATSAPP_TO")

    client = Client(account_sid, auth_token)

    msg = client.messages.create(
        body=message,
        from_=from_whatsapp,
        to=to_whatsapp
    )

    print("📤 Sent:", msg.sid)
