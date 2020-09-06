import os
from typing import Dict, List
from dotenv import load_dotenv
import re
from fastapi import FastAPI, Form
import httpx
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
load_dotenv()
client = httpx.AsyncClient()


async def sendEmail(from_number:str, body: str) -> int:
    subject = f"New SMS from {from_number}"
    headers = {
        'authorization': f"Bearer {os.getenv('SENDGRID_API_KEY')}",
        'content-type': "application/json"
    }
    req = {
        "personalizations": [{"to": {"email": os.getenv('FROM_EMAIL')}}],
        "from": {"email": os.getenv('FROM_EMAIL')},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}]
    }
    resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=req, headers=headers)
    return resp.status_code


@app.post("/hook")
async def process_sms(From: str = Form(...), Body: str = Form(...)) -> str:
    """
    Body of SMS must be like this
    `From` and `Body` will be taken from the Webhook Payload of Twilio SMS Webhook\n
    `"to:test@example.com,sub:Any Relevant Subject,msg:Any Relevant Message"`.
    """
    # pattern = r"to:(.*?),sub:(.*),msg:(.*)"
    # match = re.search(pattern, Body)
    # to_email = match.group(1)
    # subject = match.group(2)
    # email_body = match.group(3)
    # emails = re.compile("[\w.]+@\w+\.[a-z]{3}").findall(to_email)
    # if len(emails) == 0:
    #     return {"msg": "Invalid Email Address(es)"}

    # email_list = [{"email": email} for email in emails]
    email_res = await sendEmail(from_number=From, body=Body)
    # resp = MessagingResponse()

    if email_res == 202:
        return "SMS forwarding was successful"
    else:
        return "SMS forwarding was unsuccessfull"