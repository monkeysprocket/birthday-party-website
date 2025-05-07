from dotenv import load_dotenv
from flask import Flask, render_template, abort, request, redirect, url_for

from .admin import requires_auth
from .exceptions import NotFoundError
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
    try:
        guest_name = db.get_guest_by_uuid(uuid)
    except NotFoundError:
        abort(404)

    rsvp_thanks = request.args.get('rsvp') == "thanks"
    return render_template('invite.html', name=guest_name, uuid=uuid, rsvp_thanks=rsvp_thanks)


@app.route("/rsvp", methods=['POST'])
def rsvp():
    uuid = request.form.get('uuid')
    rsvp = request.form.get('rsvp')
    message = request.form.get('message', '')

    db.update_guest_rsvp(uuid=uuid, rsvp=rsvp, message=message)

    return redirect(url_for('invite', uuid=uuid, rsvp="thanks"))


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
