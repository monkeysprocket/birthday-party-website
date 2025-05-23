import os
import traceback

import boto3
from botocore.exceptions import ClientError

from .logger import create_single_file_logger

ses = boto3.client("ses", region_name=os.environ["AWS_REGION"])
logger = create_single_file_logger()


def send_invite_email(name: str, email: str, invite_id: str) -> None:
    logger.debug("trying to send invite to %s", email)
    subject = "You're Invited!"
    link = f"{os.environ['SITE_BASE_URL']}/invite/{invite_id}"
    body_text = f"Hi {name},\n\nYou're invited! Click your personal invite link to RSVP:\n{link}\n\nSee you there!"
    body_html = f"""
    <html>
        <body>
            <p>Hi {name},</p>
            <p>You're invited! Click your personal invite link to RSVP:<br>
            <a href="{link}">{link}</a></p>
            <p>See you there!</p>
        </body>
    </html>
    """

    from_email = f"{os.environ.get('EMAIL_FROM_NAME')} <{os.environ['EMAIL_FROM']}>"

    try:
        ses.send_email(
            Source=from_email,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": body_text},
                    "Html": {"Data": body_html},
                }
            }
        )
        logger.debug("successfully sent invite to %s", email)
    except ClientError as e:
        logger.error("Failed to send invite to %s\n%s\n%s", email, repr(e), traceback.format_exc())
