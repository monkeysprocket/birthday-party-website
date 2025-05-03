from flask import Flask, render_template, abort, request, redirect, url_for
import sqlite3
from uuid import UUID

app = Flask(__name__)


@app.route("/invite/<uuid>")
def invite(uuid: UUID):
    guest_name = get_guest_by_uuid(uuid)
    if not guest_name:
        abort(404)
    rsvp_thanks = request.args.get('rsvp') == "thanks"
    return render_template('index.html', name=guest_name, uuid=uuid, rsvp_thanks=rsvp_thanks)


def get_guest_by_uuid(uuid: UUID) -> str | None:
    conn = sqlite3.connect('guests.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM guests WHERE uuid = ?", (uuid,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


@app.route("/rsvp", methods=['POST'])
def rsvp():
    uuid = request.form.get('uuid')
    rsvp = request.form.get('rsvp')
    message = request.form.get('message', '')

    conn = sqlite3.connect('guests.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE guests 
        SET 
            rsvp_status = ?,
            rsvp_message = ?
        WHERE uuid = ?
    """,
    (rsvp, message, uuid),
    )

    conn.commit()
    conn.close()

    return redirect(url_for('invite', uuid=uuid, rsvp="thanks"))