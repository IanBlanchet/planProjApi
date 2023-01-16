# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from app.config import Config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Response, redirect, request, url_for
import urllib.parse

def sendmail(sender, receiver ):
    message = Mail(
        from_email=sender,
        to_emails=receiver,
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)



def sendPasswordResetEmail(sender, user, token, domain):
    
       
    url = domain+'/newpassword/?' + urllib.parse.urlencode({'token':token, 'email':user.email })
    
    print(url)

    message = Mail(
        from_email=sender,
        to_emails=user.email,
        subject='PlanProj - Réinitialiser ton mot de passe',
        html_content=f'<strong>Bonjour, { user.username} </strong>\
                    <p>\
                    Pour réinitialiser ton mot de passe dans l\'application de planification\
                    <a href={ url }>\
                    clique ici\
                    </a>.\
                    </p>)'
    )
    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)