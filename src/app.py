import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

from .admin import requires_auth
from .model import Model
from .send_email import send_invite_email

load_dotenv()

app = Flask(__name__)
db = Model()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/invite/<uuid>")
def invite(uuid: str):
    return render_template(
        'invite.html',
        API_URL=os.environ["API_URL"],
    )


@app.route("/admin", methods=["GET"])
@requires_auth
def admin():
    guests = db.get_all_guests()
    return render_template(
        'admin.html',
        guests=guests,
        message=request.args.get("message"),
        error=request.args.get("error"),
    )


@app.route("/admin/add_guest", methods=["POST"])
def admin_new_guest():
    name = request.form.get("name")
    email = request.form.get("email")
    if name and email:
        new_guest_uuid = db.add_guest(name, email)
        try:
            send_invite_email(name, email, new_guest_uuid)
        except Exception as e:
            return redirect(url_for("admin", error=f"Failed to send invite to {email}. {e}"))
        else:
            return redirect(url_for("admin", message=f"Invite sent to {email}."))
