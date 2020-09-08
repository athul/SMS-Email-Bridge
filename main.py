import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form , Response
import httpx
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
load_dotenv()


@app.post("/hook")
async def process_sms(From: str = Form(...), Body: str = Form(...)) -> str:
    subject = f"New SMS from {From}"
    headers = {
        'authorization': f"Bearer {os.getenv('SENDGRID_API_KEY')}",
        'content-type': "application/json"
    }
    req = {
        "personalizations": [{"to": [{"email": "athulca08@gmail.com"}],}],
        "from": {"email": os.getenv('FROM_EMAIL')},
        "subject": subject,
        "content": [{"type": "text/plain", "value": Body}]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=req, headers=headers)
    msgresp = MessagingResponse()
    if resp.status_code == 202:
        msgresp.message("Thank You, your SMS has been received")
        return Response(content=str(msgresp),media_type="application/xml")
    else:
        msgresp.message("SMS has not been forwarded")
        return Response(content=str(msgresp),media_type="application/xml")