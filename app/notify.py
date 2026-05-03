import os
from twilio.rest import Client


def send_whatsapp(message: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM")
    to_whatsapp = os.getenv("TWILIO_WHATSAPP_TO")

    if not all([account_sid, auth_token, from_whatsapp, to_whatsapp]):
        print("❌ Missing Twilio config")
        return

    try:
        client = Client(account_sid, auth_token)

        msg = client.messages.create(
            body=message,
            from_=from_whatsapp,
            to=to_whatsapp
        )

        print("✅ WhatsApp sent:", msg.sid)

    except Exception as e:
        print("❌ Twilio Error:", str(e))
