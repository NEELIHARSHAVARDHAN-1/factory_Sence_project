from twilio.rest import Client
import os


def send_whatsapp(message: str):
    try:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_ = os.getenv("TWILIO_WHATSAPP_FROM")
        to = os.getenv("TWILIO_WHATSAPP_TO")

        if not all([sid, token, from_, to]):
            print("❌ Missing Twilio env variables")
            return

        client = Client(sid, token)

        msg = client.messages.create(
            body=message,
            from_=from_,
            to=to,
        )

        print("📩 WhatsApp sent:", msg.sid)

    except Exception as e:
        print("❌ WhatsApp error:", e)