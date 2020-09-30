
import os
import json
import datetime

import waitress
import flask
import flask_dance.contrib.google
import jinja2


# Setup stuff
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "true"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app = flask.Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["TEMPLATES_AUTO_RELOAD"] = True
google_bp = flask_dance.contrib.google.make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/login")
app.jinja_env.undefined = jinja2.StrictUndefined


# Read the necessary info for Google logins
google_config = json.load(open('google_config.json', 'r'))
app.config["GOOGLE_OAUTH_CLIENT_ID"] = google_config["client_id"]
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = google_config["secret"]


# Read in a .json file and use it as a simple database
DB_FILE = 'database.json'
if not os.path.exists(DB_FILE):
    # database file doesn't exist, make an empty one
    database = {}
else:
    database = json.load(open(DB_FILE, 'r+'))


# Call this to write the database back to the file
def save():
    json.dump(database, open(DB_FILE, 'w'), indent=2)
    

def get_user():
    # If the user isn't logged in, send them to the login page
    if not flask_dance.contrib.google.google.authorized:
        return flask.redirect(flask.url_for("google.login"))

    # Get the login info (email, name, etc.)
    response = flask_dance.contrib.google.google.get("/oauth2/v1/userinfo")
    assert response.ok, response.text
    user_info = response.json()
    return user_info


@app.route("/")
def index():
    # Show a basic landing page
    return flask.render_template("landing_page.html")


def get_properties_for_user(email):
    # Get all the properties for a user in the database
    if email not in database:
        database[email] = {
            "properties": []
        }
        save()
    return database[email]["properties"]


def add_property_to_user(email, property):
    # Add a property object to a user in the database
    if email not in database:
        database[email] = {
            "properties": []
        }
    database[email]["properties"].append(property)
    save()


@app.route("/properties")
def properties():
    # Make sure the user is logged in
    login = get_user()
    if not isinstance(login, dict):
        # User is not logged in, redirect them to google
        return login

    # Get the user's info
    email = login["email"]
    name = login["name"]

    # Get their entry from the database (based on their email)
    properties = get_properties_for_user(email)
    return flask.render_template("properties.html", name=name, properties=properties)


@app.route('/property', methods=["POST"])
def add_property():
    # Make sure the user is logged in
    login = get_user()
    if not isinstance(login, dict):
        # User is not logged in, redirect them to google
        return login

    # Save the property on the user
    email = login["email"]
    add_property_to_user(email, {
        "address": flask.request.values["address"],
        "tenant_company": flask.request.values["tenant_company"],
        "added": datetime.datetime.now().strftime("%d/%m/%Y")
    })

    # Refresh the page
    return flask.redirect(flask.url_for("properties"))


def main():
    waitress.serve(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()