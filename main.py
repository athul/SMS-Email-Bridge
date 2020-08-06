import os
from dotenv import load_dotenv
import re
from fastapi import FastAPI, Form
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

app = FastAPI()
load_dotenv()

def sendEmail(to:str,subject:str,body:str) -> str:
    message = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        subject=subject,
        to_emails=to,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient()
        resp = sg.send(message)
        return str(resp.status_code)
    except Exception as exc:
        return str(exc)
        print(f"Could not send email to {to} due {str(exc)}")

@app.post("/hook")
async def process_sms(From:str = Form(...), Body:str = Form(...)):
    """Body of SMS must be like this
    `From` and `Body` will be taken from the Webhook Payload of Twilio SMS Webhook\n
    `"TO:test@example.com,SUB:Any Relevant Subject,MSG:'Any Relevant Message'"`. The MSG part must be enclosed in single quotes(`'`)
    """
    pattern = r"TO:(.*?),SUB:(.*?),MSG:('.*?')"
    match = re.search(pattern,Body)
    to_email = match.group(1)
    subject = match.group(2)
    email_body = match.group(3).replace("'","")
    email_res = sendEmail(to=to_email,subject=subject,body=email_body)
    if email_res == "202":
        client = Client()
        message = client.messages.create(
            to=From,
            body=f"Email to {to_email} is Sent",
            from_=os.getenv("TWILIO_PHONE_NUMBER")
        )
        return {"message":f"Successfully Sent Message to {From}"}
    else:
        return {"error":f"Unsuccessfull due to {email_res}"}