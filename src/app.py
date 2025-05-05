from flask import Flask, render_template, abort, request, redirect, url_for
from uuid import UUID
from dotenv import load_dotenv
import os

from admin import requires_auth
from model import Model
from exceptions import NotFoundError

load_dotenv()

app = Flask(__name__)
db = Model(
    connection_string=os.environ.get("CONNECTION_STRING"),
    admin_password=os.environ.get("ADMIN_PASSWORD"),
)


@app.route("/invite/<uuid>")
def invite(uuid: UUID):
    try:
        guest_name = db.get_guest_by_uuid(uuid)
    except NotFoundError:
        abort(404)

    rsvp_thanks = request.args.get('rsvp') == "thanks"
    return render_template('index.html', name=guest_name, uuid=uuid, rsvp_thanks=rsvp_thanks)


@app.route("/rsvp", methods=['POST'])
def rsvp():
    uuid = request.form.get('uuid')
    rsvp = request.form.get('rsvp')
    message = request.form.get('message', '')

    db.update_guest_rsvp(uuid=uuid, rsvp=rsvp, message=message)

    return redirect(url_for('invite', uuid=uuid, rsvp="thanks"))


@app.route("/admin")
@requires_auth
def admin():
    guests = db.get_all_guests()
    return render_template('admin.html', guests=guests)
