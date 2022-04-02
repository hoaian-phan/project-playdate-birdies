""" Server for playdate birdies apps """

from flask import (Flask, render_template, request, redirect, flash, session, jsonify)
from model import connect_to_db, db
from jinja2 import StrictUndefined
from datetime import datetime, date
from passlib.hash import argon2
from flask_mail import Mail, Message
import crud
import os

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.jinja_env.undefined = StrictUndefined
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = "do-not-reply@playdatebirdies.com"
app.config['MAIL_MAX_EMAILS'] = 3


mail = Mail(app)

US_STATES = {
  "AL": "Alabama",
  "AK": "Alaska",
  "AZ": "Arizona",
  "AR": "Arkansas",
  "CA": "California",
  "CO": "Colorado",
  "CT": "Connecticut",
  "DE": "Delaware",
  "FL": "Florida",
  "GA": "Georgia",
  "HI": "Hawaii",
  "ID": "Idaho",
  "IL": "Illinois",
  "IN": "Indiana",
  "IA": "Iowa",
  "KS": "Kansas",
  "KY": "Kentucky",
  "LA": "Louisiana",
  "ME": "Maine",
  "MD": "Maryland",
  "MA": "Massachusetts",
  "MI": "Michigan",
  "MN": "Minnesota",
  "MS": "Mississippi",
  "MO": "Missouri",
  "MT": "Montana",
  "NE": "Nebraska",
  "NV": "Nevada",
  "NH": "New Hampshire",
  "NJ": "New Jersey",
  "NM": "New Mexico",
  "NY": "New York",
  "NC": "North Carolina",
  "ND": "North Dakota",
  "OH": "Ohio",
  "OK": "Oklahoma",
  "OR": "Oregon",
  "PA": "Pennsylvania",
  "RI": "Rhode Island",
  "SC": "South Carolina",
  "SD": "South Dakota",
  "TN": "Tennessee",
  "TX": "Texas",
  "UT": "Utah",
  "VT": "Vermont",
  "VA": "Virginia",
  "WA": "Washington",
  "WV": "West Virginia",
  "WI": "Wisconsin",
  "WY": "Wyoming"
}

AGE_GROUP = ["infants", "toddlers", "preschoolers", "kindergarteners",
            "elementary", "middleschool", "highschool", "any age"]

ACTIVITIES = ["Draw with chalk", "Go on a scavenger hunt", "Kick a ball", "Blow bubbles",
            "Play tag", "Tug of war", "Fly a kite", "Squirt water guns", "Basket ball", 
            "Play with sand", "Have a race", "Make paper airplanes", "Water balloon t-ball",
            "Hula hoop", "Painting", "Collect leaves", "Jumping rope", "Bag jumping", 
            "Bike/scooter riding"]


# 1. Homepage route
@app.route("/")
def homepage():
    """ Display homepage """
    # Get homepage base url

    return render_template("homepage.html", age_groups = AGE_GROUP, today = date.today())

# 2a. Sign up page with GET to render template with the sign up form
@app.route("/signup")
def sign_up():
    """ Render the sign up page with the form in it"""

    return render_template("signup.html")


# 2b. Create an account route
@app.route("/signup", methods = ["POST"])
def create_user():
    """ Create a new user """
    # Using POST request, get input from the sign up form
    fname = request.form.get("first")
    lname = request.form.get("last")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_pw = request.form.get("confirm_password")

    # Check if confirm password matches with password, if not, restart the sign up form
    # Use Javascript to add event handler and prevent submitting the form
    if password != confirm_pw:
        flash("Passwords don't match. Please try again.")
        return redirect("/signup")

    # Otherwise, get user object by the input email
    user = crud.get_user_by_email(email)

    # Hash password for security reason
    hashed = argon2.hash(password)
    del password
    del confirm_pw

    # If this user doesn't exist in database, create and add this new user to database
    if not user:
        new_user = crud.sign_up(fname, lname, email, hashed)
        db.session.add(new_user)
        db.session.commit()
        # Flash message and add user_id to session 
        flash(f"Hi {new_user.fname}, welcome to Playdate Birdies community.")
        session["user_id"] = new_user.user_id 
        session["user_fname"] = new_user.fname
        if "event_id" in session:
            event = crud.get_event_by_id(session["event_id"])
            return render_template("register.html", event=event)
        # return user to their previous page (hosting or register or homepage) - add later
        return redirect("/")
    else: # if user exists, flash message and restart sign up form
        flash("This email has already been used. Please try a different email.")
        return redirect("/signup")


# 3a. Login with GET to render template login with the login form
@app.route("/login")
def login_get():
    """ Render the login page with the form in it"""

    if "user_id" in session:
        flash("You are already logged in.")
        return redirect ("/")
    
    return render_template("login.html")

# 3b. Login route with POST 
@app.route("/login", methods = ["POST"])
def login():
    """ User login """

    # Using POST method, get the input email and password from the log in form
    email = request.form.get("email")
    password = request.form.get("password")
    # remember = request.form.get("remember_me")

    # Get the user object by input email
    user = crud.get_user_by_email(email)

    # If this user exists in database, check if password matches; if yes, log in
    if user:
        if argon2.verify(password, user.password):
            flash(f"Hi {user.fname}, welcome back.")
            session["user_id"] = user.user_id
            session["user_fname"] = user.fname
            if "event_id" in session:
                event = crud.get_event_by_id(session["event_id"])
                return render_template("register.html", event=event)
            # return user to their previous page (hosting or register or homepage) - add later
            return redirect("/")
        else: # if not, flash message
            flash("This email and password combination is incorrect.") #or click Forget password
    else:
        flash("This email and password combination is incorrect.") #or click Forget email address
    
    return redirect("/login")

# Render the form to reset password
@app.route("/forget_pw")
def forget_password():
    """ Render the reset password form"""

    return render_template("reset_password.html")

# Reset password
@app.route("/reset_pw", methods=["POST"])
def reset_password():
    """ Reset password"""

    # Using POST request, get input from the reset password form
    fname = request.form.get("first")
    lname = request.form.get("last")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_pw = request.form.get("confirm_password")

    # Check if confirm password matches with password, if not, restart the form
    if password != confirm_pw:
        flash("Passwords don't match. Please try again.")
        return redirect("/reset_pw")

    # Hash password for security reason
    hashed = argon2.hash(password)
    del password
    del confirm_pw

    # Check if name and email address match with a current user
    user = crud.get_user_by_name_email(fname, lname, email)
    if user:
        user.password = hashed
        db.session.commit()
        flash("Successfully reset your password. ")
        return redirect("/login")
    else:
        flash("Name and email addres do not match our record. Please try again or sign up for a new account.")
        return redirect("/forget_pw")

# 4. Log out
@app.route("/logout")
def logout():
    """ Log out """

    if "user_id" in session:
        session.clear()
        flash("You were logged out.")
    
    return redirect("/")

# 5. User profile
@app.route("/profile")
def show_profile():
    """ Show user profile """
    if "user_id" not in session:
        return redirect("/")
    # Get user object by user_id
    user = crud.get_user_by_id(session["user_id"])
    # Iterate through each event this user is the host, and make a pass and future events
    past_host_events = []
    future_host_events = []
    for event in user.events:
        if crud.is_future(event):
            future_host_events.append(event)
        else:
            past_host_events.append(event)
    # Iterate through each event this user is the participant, and make a pass and future events
    past_guess_events = []
    future_guess_events = []
    for registration in user.registrations:
        if crud.is_future(registration.event):
            future_guess_events.append(registration)
        else:
            past_guess_events.append(registration)
    
    return render_template("user_profile.html", user=user, past_host=past_host_events, future_host=future_host_events,
                                                past_guess= past_guess_events, future_guess=future_guess_events)
    
    
# 4a. Rendering the Hosting papge with GET
@app.route("/host")
def host():
    """ Display host form"""

    if "user_id" not in session:
        flash("Please log in to host a playdate.")
        return redirect("/login")
    
    return render_template("hosting.html", today = date.today(), states=US_STATES, age_groups=AGE_GROUP, activities=ACTIVITIES)


# 4b. Hosting page with POST to create an event
@app.route("/host", methods=["POST"])
def hosting():
    """ Host a playdate"""

    # Get host_id from session
    host_id = session["user_id"]
    # Get input from the form
    title = request.form.get("title")
    description = request.form.get("description")
    name = request.form.get("location")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    date = request.form.get("date")
    start = request.form.get("start")
    end = request.form.get("end")
    age_group = request.form.get("age_group")
    standard_activities = request.form.getlist("activity")
    other_activity = request.form.get("otherActivity")
    equipment_names = request.form.getlist("item")
    equipment_quantities = request.form.getlist("quantity")


    # Query this input location to check it is already in database
    input_location = crud.get_location_by_name_and_address(name=name, address=address)
    # If not, create a new location object and add to database
    if not input_location:
        input_location = crud.create_new_location(name, address, city, zipcode, state)
        db.session.add(input_location)
        db.session.commit()

    # Create a new event object and add to database
    new_event = crud.host_a_playdate(host_id, title, description, input_location.location_id,
                                    date, start, end, age_group)
    db.session.add(new_event)
    db.session.commit()

    # Process activity inputs
    other_activities = other_activity.split(", ")
    # check to see if "other" is in the list of standard_activities
    if "other" in standard_activities:
        activities = standard_activities[:-1] + other_activities
    else:
        activities = standard_activities[:] + other_activities
    # Create activity and add to database
    for one_activity in activities:
        activity = crud.get_activity_by_name(one_activity)
        if not activity:
            activity = crud.create_an_activity(one_activity)
            db.session.add(activity)
            db.session.commit()
        # Create association between activity and event
        activity_event = crud.create_activity_event_asso(activity.activity_id, new_event.event_id)
        db.session.add(activity_event)
        db.session.commit()
    
    # Add equipment and its quantity to database
    for i, equipment in enumerate(equipment_names):
        equipment = crud.create_an_equipment(new_event.event_id, equipment, equipment_quantities[i])
        db.session.add(equipment)
        db.session.commit()

    flash(f"{new_event.host.fname}, your playdate {new_event.title} is scheduled on {new_event.date} from {new_event.start_time} to {new_event.end_time} at {new_event.location.name}.")
    flash("Congratulations! You will be an awesome host!")
    
    return redirect("/profile")


# 6b. Update coordinates of location to database
@app.route("/update_location_details", methods = ["POST"])
def update_location_details():
    """ Update the location coordinates in the database """
    # Get info from the fetch call
    lat = request.json.get("lat")
    lng = request.json.get("lng")
    photo = request.json.get("photo")
    name = request.json.get("name")
    address = request.json.get("address")

    # Get the location object
    location = crud.get_location_by_name_and_address(name, address)
    # Update the coordinates
    location.lat = lat
    location.lng = lng
    location.photo = photo
    db.session.commit()

    return {"status": "ok"}

# Cancel an event
@app.route("/cancel_event", methods=["POST"])
def cancel_event():
    """ Cancel an event you created """
    # Get event_id from the form
    event_id = request.form.get("event_id")
    # Get event object from event_id
    event = crud.get_event_by_id(event_id)
    # Get the homepage url root
    url_root = request.url_root
    # Check if this is the host of the event
    if event.host.user_id == session["user_id"]:
        # Send email notifications to the participants
        if event.registrations:
            emails = [registration.user.email for registration in event.registrations]
            msg = Message(f"Your {event.title} is canceled", bcc=emails)
            homepage_url = f"<br><a href={url_root}>Playdate Birdies</a>"
            msg.html = f"We are sorry your playdate got canceled. Please visit {homepage_url} to see other events."
            mail.send(msg)

        # Delete all registrations for this event
        crud.delete_registrations(event_id)

        # Delete all activity association for this event
        crud.delete_activity_event_asso(event_id)
        db.session.commit()
    
        #Delete this event
        db.session.delete(event)
        db.session.commit()
        flash("You successfully deleted your playdate.")
    else:
        flash("Only the host can cancel a playdate.")

    return redirect("/profile")


# 5. Search for a playdate
@app.route("/search")
def search():
    """ Search for a playdate """

    # Get user input from the search form
    city_zipcode = request.args.get("city_zipcode")
    date = request.args.get("date")
    age_group = request.args.get("age_group")
    activity = request.args.get("activity")

    # Process date string input
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()

    # Get a list of search results
    events = crud.get_events_by_inputs(city_zipcode=city_zipcode, date=date, age_group=age_group, activity=activity)

    return render_template("search_results.html", events=events)


# 6. Display event details
@app.route("/events")
def show_details():
    """ Show event details """

    # Get the event_id from fetch call
    event_id = request.args.get("event_id")

    # Get the event by event_id
    event = crud.get_event_by_id(event_id)
    
    # Check if this user_id already register for this event
    if "user_id" in session:
        registration = crud.get_registration(event_id, session["user_id"])
    if registration:
        registered = True
    else:
        registered = False

    # Remake event dictionary for jsonify
    event = {
        "event_id": event.event_id,
        "host": event.host.fname + " " + event.host.lname,
        "host_id": event.host.user_id,
        "title": event.title,
        "description": event.description,
        "date": str(event.date),
        "start_time": str(event.start_time),
        "end_time": str(event.end_time),
        "age_group": event.age_group,
        "location_id": event.location.location_id,
        "location": event.location.name,
        "address": event.location.address,
        "city": event.location.city,
        "zipcode": event.location.zipcode,
        "state": event.location.state,
        "lat": event.location.lat,
        "lng": event.location.lng,
        "activity_list": [activity.name for activity in event.activities],
        "attendants": [(registration.user.fname + " " + registration.user.lname) for registration in event.registrations],
        "equipments": [(equipment.name + ": " + str(equipment.quantity)) for equipment in event.equipments],
        "attendant_ids": [registration.user.user_id for registration in event.registrations],
        "is_registered": registered,
    }
 
    return jsonify(event)

# 7a. Render the register page
@app.route("/attend")
def render_register():
    """ Render register page """
    # Get event_id from the form and save in session
    event_id = request.args.get("event_id")
    session["event_id"] = event_id
    
    # If user is not logged in, return to login page
    if "user_id" not in session:
        flash("Please log in to register")
        return redirect("/login")

    # Get event object by event_id
    event = crud.get_event_by_id(event_id)

    return render_template("register.html", event=event)

# Get participants of the event
@app.route("/participants.json")
def get_participants_json():
    """ Return a JSON response with all participants"""

    # Get event object by event_id
    event = crud.get_event_by_id(session["event_id"])
    # Get the total count and list of participants
    total_count = 0
    attendants = []
    for registration in event.registrations:
        total_count += registration.num_people
        attendants.append(registration.user.fname + " " + registration.user.lname)

    return jsonify({"counts": total_count, "participants": attendants})

# 7a Register for a playdate using AJAX request from REACT form
@app.route("/register_name", methods = ["POST"])
def register_name():
    """ Register user for an event with name and number of people """
    # Get inputs from the AJAX request. 
    name = request.get_json().get("name")
    num_people = int(request.get_json().get("num_people"))
    # Get user_id and event_id from the form
    user_id = session["user_id"]
    event_id = session["event_id"]
    # Get user obj and event obj
    event = crud.get_event_by_id(event_id)
    user = crud.get_user_by_id(user_id)
    # Get the registration by this user_id and event_id
    registration = crud.get_registration(event_id, user_id)
    # Check if this user has already registered for this event
    if registration:
        return jsonify({"success": False})
    # If not register, create a new registration and add to database
    registration = crud.create_new_registration(event_id, user_id, num_people)
    db.session.add(registration)
    db.session.commit()
    # Create registration string
    new_registration = {
        "name": name,
        "num_people": num_people,
        "event_title": registration.event.title,
    }
    # Get the url root
    url_root = request.url_root
    # Send email updates to the host every time there is a new registration
    msg = Message(f"Your {event.title} got a new registration", recipients=[event.host.email])
    profile_url = f"<br><a href={url_root}/profile>your profile</a>"
    msg.html = f"{user.fname} {user.lname} has just registered to join your playdate {event.title}. Visit {profile_url} to see more."
    mail.send(msg)
    
    return jsonify({"success": True, "registration": new_registration})


# Cancel an event registration
@app.route("/cancel_registration", methods=["POST"])
def cancel_registration():
    """ Cancel an event registration """
    # Get event_id from the form
    event_id = request.form.get("event_id")
    event = crud.get_event_by_id(event_id)
    # Get the url root
    url_root = request.url_root
    # If this registration exists, delete it
    registration = crud.get_registration(event_id, session["user_id"])
    if registration:
        # Send email notification to the host of the cancelation
        msg = Message(f"Update for your {registration.event.title}", recipients=[registration.event.host.email])
        profile_url = f"<br><a href={url_root}/profile>your profile</a>"
        msg.html = f"{registration.user.fname} {registration.user.lname} has just canceled their registration for your playdate {registration.event.title}. Visit {profile_url} to see more."
        mail.send(msg)
        # Delete the registration
        db.session.delete(registration)
        db.session.commit()
        flash("You successfully deleted your registration.")
    else:
        flash("You did not register for this playdate.")

    return redirect("/profile")

# Follow a user
@app.route("/follow")
def follow():
    """ Follow a user """
    # Get user1_id from session and retrieve user1 object
    user1_id = session["user_id"]
    user1 = crud.get_user_by_id(user1_id)
    # Get user2_id from the url and retrieve user2 object
    user2_id = request.args.get("user2_id")
    user2 = crud.get_user_by_id(user2_id)
    # Check if user1 and user2 are friends already
    if user1 in user2.get_all_friends():
        return jsonify({"success": False, "friend": user2.fname + " " + user2.lname})
    # User1 follows user2
    user1.following.append(user2)
    db.session.commit()

    return jsonify({"success": True, "friend": user2.fname + " " + user2.lname})


# Invite friends to join playdates
@app.route("/invite")
def invite_friends():
    """ Choose friends from the list to invite """
    # Get user_id and event_id from the form
    user_id = session["user_id"]
    event_id = request.args.get("event_id")
    # Get user obj and event obj
    event = crud.get_event_by_id(event_id)
    user = crud.get_user_by_id(user_id)
    friend_list = user.get_all_friends()

    return render_template("invitation.html", event=event, user=user, friend_list=friend_list)


# Send email invitation to friends
@app.route("/send_invitation")
def send_invitation():
    """ Send email to user """
    # Get info from session
    user_id = session["user_id"]
    event_id = session["event_id"]
    # Get user obj and event obj
    event = crud.get_event_by_id(event_id)
    user = crud.get_user_by_id(user_id)
    #Get inputs from the form
    recipients = request.args.getlist("friend")
    event_url = request.args.get("event_info")
    message_body = request.args.get("message")
    # Make the hyperlink by concatenating the root url and event url
    url_root = request.url_root
    event_url = url_root + event_url 
    message_body += f"<br><a href='{event_url}'>{event.title}</a>"
    # Create an email notification and send
    msg = Message(f'{user.fname} {user.lname} recommends you check out this playdate', bcc=recipients)
    msg.html = message_body
    mail.send(msg)
    flash("You successfully sent invitations to this playdate.")
    return redirect("/profile")


# Route to render Calendar page
@app.route("/calendar")
def show_calendar():
    """ Show the personal calendar with events"""

    user_id = session["user_id"]
    user = crud.get_user_by_id(user_id)
    # Get all attending events and set color to purple
    calendar_events = crud.get_events_by_userid(user_id)
    events_dict = []
    for event in calendar_events:
        events_dict.append(
            {
                "title": event.title,
                "start": str(event.date) + "T" + str(event.start_time),
                "end": str(event.date) + "T" + str(event.end_time),
                "color": "purple"
            }
        )
    # Then add all hosting events and set color to green
    for event in user.events:
        events_dict.append(
            {
                "title": event.title,
                "start": str(event.date) + "T" + str(event.start_time),
                "end": str(event.date) + "T" + str(event.end_time),
                "color": "green"
            }
        )
    
    return render_template("calendar.html", cal_events=events_dict)


# Send reminder email route
@app.route("/reminder")
def reminder():
    """ Send email reminders about an upcoming events"""

    # Get a list of users that have events tomorrow
    users = crud.get_users_of_tomorrow_events(date.today())
    print("\n" * 5, "Users from query: ", users)
    
    # Get the url root
    url_root = request.url_root

    # Send bulk emails:
    # with mail.connect() as conn:
    #     for user in users:
    #         message = f"Don't need to wait long, your playdate is tomorrow! Log in to <br><a href={url_root}/profile>your profile</a> to see details."
    #         subject = "You have an upcoming playdate tomorrow"
    #         msg = Message(bcc=[user.email],
    #                     html=message,
    #                     subject=subject)

    #         conn.send(msg)
    
    # Get email list
    recipients = []
    for user in users:
        recipients.append(user.email)
    print("email list: ", recipients)

    # Create an email notification and send
    msg = Message("You have an upcoming playdate tomorrow", bcc=recipients)
    msg.html = f"Don't need to wait long, your playdate is tomorrow! Log in to <br><a href={url_root}/profile>your profile</a> to see details."
    mail.send(msg)

    return "Sent"

if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)