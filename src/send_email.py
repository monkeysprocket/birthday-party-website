import smtplib
import os
from email.mime.text import MIMEText
from email.utils import formataddr


def send_invite_email(name, email, invite_id):
    subject = "You're Invited!"
    link = f"{os.environ['SITE_BASE_URL']}/invite/{invite_id}"
    body = f"Hi {name},\n\nYou're invited! Click your personal invite link to RSVP:\n{link}\n\nSee you there!"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr((os.environ.get('EMAIL_FROM_NAME'), os.environ['EMAIL_FROM']))
    msg['To'] = email

    with smtplib.SMTP(os.environ['EMAIL_HOST'], int(os.environ['EMAIL_PORT'])) as server:
        server.starttls()
        server.login(os.environ['EMAIL_USERNAME'], os.environ['EMAIL_PASSWORD'])
        server.sendmail(msg['From'], [email], msg.as_string())
