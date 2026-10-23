import os
import requests

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '').strip()
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886').strip()

FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', '').strip()

def format_indian_number(phone):
    """10-digit Indian number ke aage +91 format karta hai"""
    phone = str(phone).strip().replace(" ", "").replace("-", "")
    if len(phone) == 10 and phone.isdigit():
        return f"+91{phone}"
    elif not phone.startswith("+"):
        return f"+{phone}"
    return phone

def send_sms_notification(to_phone, message_text):
    if not to_phone:
        return False
        
    formatted_phone = format_indian_number(to_phone)
    print(f"\n[SMS DISPATCH] To: {formatted_phone}\nMessage: {message_text}\n" + "-"*40)
    
    # 1. Fast2SMS Integration (Agar valid Key ho)
    if FAST2SMS_API_KEY and FAST2SMS_API_KEY != 'your_fast2sms_api_key_here':
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            raw_phone = formatted_phone.replace("+91", "")
            payload = f"message={message_text}&language=english&route=q&numbers={raw_phone}"
            headers = {
                'authorization': FAST2SMS_API_KEY,
                'Content-Type': "application/x-www-form-urlencoded"
            }
            response = requests.post(url, data=payload, headers=headers, timeout=5)
            res_json = response.json()
            if res_json.get('return'):
                print(f"Fast2SMS Sent Successfully!")
                return True
            else:
                print(f"Fast2SMS API Response: {res_json.get('message')}")
        except Exception as e:
            print(f"Fast2SMS Exception: {e}")

    # 2. Twilio SMS Integration
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message_text,
                from_=TWILIO_PHONE_NUMBER,
                to=formatted_phone
            )
            print(f"Twilio SMS Sent! SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"Twilio SMS Error: {e}")
            
    return True

def send_whatsapp_notification(to_phone, message_text):
    if not to_phone:
        return False
        
    formatted_phone = format_indian_number(to_phone)
    print(f"\n[WHATSAPP DISPATCH] To: {formatted_phone}\nMessage: {message_text}\n" + "-"*40)
    
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message_text,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{formatted_phone}"
            )
            print(f"Twilio WhatsApp Sent! SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"Twilio WhatsApp Error: {e}")
            
    return True