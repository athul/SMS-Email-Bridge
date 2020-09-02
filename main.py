import os
from typing import Dict,List
from dotenv import load_dotenv
import re
from fastapi import FastAPI, Form
import httpx
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
load_dotenv()
client = httpx.AsyncClient()


async def sendEmail(to: List, subject: str, body: str) -> int:
    headers = {
        'authorization': f"Bearer {os.getenv('SENDGRID_API_KEY')}",
        'content-type': "application/json"
    }
    req = {
        "personalizations": [{"to": to}],
        "from": {"email": os.getenv('FROM_EMAIL')},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}]
    }

    resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=req, headers=headers)
    print(resp.status_code)
    return resp.status_code


@app.post("/hook")
async def process_sms(From: str = Form(...), Body: str = Form(...)) -> Dict:
    """
    Body of SMS must be like this
    `From` and `Body` will be taken from the Webhook Payload of Twilio SMS Webhook\n
    `"TO:test@example.com,SUB:Any Relevant Subject,MSG:'Any Relevant Message'"`. The MSG part must be enclosed in single quotes(`'`)
    """
    pattern = r"to:(.*?)sub:(.*),msg:(.*)"
    match = re.search(pattern, Body)
    to_email = match.group(1)
    subject = match.group(2)
    email_body = match.group(3)
    emails = re.compile("[\w.]+@\w+\.[a-z]{3}").findall(to_email)
    if len(emails) == 0:
        return {"msg":"Invalid Email Address(es)"}
    email_list = [{"email":email} for email in emails]
    print(email_list)
    email_res = await sendEmail(to=email_list, subject=subject, body=email_body)
    print(f"Main Endpoint resp of Email - {email_res}")
    # url = f"https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json"
    # auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    resp = MessagingResponse()

    if email_res == 202:
        resp.message(f"Email to {emails} was successful")
        return {"message": f"Successfully Sent SMS to {From}"}
    else:
        resp.message(f"Email to {emails} was unsuccessful")
        return {"error": f"Unsuccessful due to {email_res}"}
