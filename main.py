import os
from dotenv import load_dotenv
import re
from fastapi import FastAPI, Form
import httpx

app = FastAPI()
load_dotenv()
print("Env Loaded")
client = httpx.AsyncClient()

async def sendEmail(to: str, subject: str, body: str) -> int:
    print("Ivide ⚡️")
    token_header = f"Bearer {os.getenv('SENDGRID_API_KEY')}"
    headers = {
        'authorization': token_header,
        'content-type': "application/json"
    }
    req = {
        "personalizations": 
        [{"to": [{"email": to}]}],
        "from": {"email": os.getenv(
        'FROM_EMAIL')}, 
        "subject": subject, 
        "content": [{"type": "text/plain", "value": body}]
        }

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=req, headers=headers)

    print("Email 😅")
    return resp.status_code


@app.post("/hook")
async def process_sms(From: str = Form(...), Body: str = Form(...)):
    """Body of SMS must be like this
    `From` and `Body` will be taken from the Webhook Payload of Twilio SMS Webhook\n
    `"TO:test@example.com,SUB:Any Relevant Subject,MSG:'Any Relevant Message'"`. The MSG part must be enclosed in single quotes(`'`)
    """
    pattern = r"TO:(.*?),SUB:(.*?),MSG:('.*?')"
    match = re.search(pattern, Body)
    to_email = match.group(1)
    subject = match.group(2)
    email_body = match.group(3).replace("'", "")
    email_res = await sendEmail(to=to_email, subject=subject, body=email_body)
    url = f"https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json"
    auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    if email_res == 202:
        print("Email Sent")
        payload = {
            "Body": f"Email to {to_email} is Sent",
            "From": os.getenv('TWILIO_PHONE_NUMBER'),
            "To": From
        }
        response = await client.post(url, data=payload, auth=auth)
        return {"message": f"Successfully Sent SMS to {From}"}
    else:
        payload = {
            "Body": f"Email to {to_email} was unsuccessfull",
            "From": os.getenv('TWILIO_PHONE_NUMBER'),
            "To": From
        }
        response = await client.post(url, data=payload, auth=auth)
        return {"error": f"Unsuccessful due to {email_res}"}
