import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form , Response
import httpx
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
load_dotenv()


# async def sendEmail(from_number:str, body: str) -> int:
#     subject = f"New SMS from {from_number}"
#     headers = {
#         'authorization': f"Bearer {os.getenv('SENDGRID_API_KEY')}",
#         'content-type': "application/json"
#     }
#     req = {
#         "personalizations": [{"to": [{"email": "athulca08@gmail.com"}],}],
#         "from": {"email": os.getenv('FROM_EMAIL')},
#         "subject": subject,
#         "content": [{"type": "text/plain", "value": body}]
#     }
#     async with httpx.AsyncClient() as client:
#         resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=req, headers=headers)
#     return resp.status_code

@app.post("/hook")
async def process_sms(From: str = Form(...), Body: str = Form(...)) -> str:
    # email_res = await sendEmail(from_number=From, body=Body)
    # print(email_res)
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
    # return resp.status_code
    msgresp = MessagingResponse()
    if resp.status_code == 202:
        msgresp.message("Thank You, your SMS has been received")
        print(resp)
        return Response(content=str(msgresp),media_type="application/xml")
    else:
        msgresp.message("SMS has not been forwarded")
        return Response(content=str(msgresp),media_type="application/xml")