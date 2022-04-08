""" Server for playdate birdies apps """

from flask import (Flask, render_template, request, redirect, flash, session, jsonify)
from model import connect_to_db, db
from jinja2 import StrictUndefined
from datetime import datetime, date, timedelta
from passlib.hash import argon2
from flask_mail import Mail, Message
from celery import Celery
import redis
import crud
import os
import re

# Flask app config
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.jinja_env.undefined = StrictUndefined
mail = Mail(app)

# Flask mail config
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = "do-not-reply@playdatebirdies.com"

mail = Mail(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

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
            "Hula hoop", "Drawing and coloring", "Collect leaves", "Jumping rope", "Bag jumping", 
            "Bike/scooter riding", "Volley ball", "Obstacle course", "Finger painting", "Singing",
            "Music time", "Dancing", "Musical chair"]


# Homepage route
@app.route("/")
def homepage():
    """ Display homepage """

    # Recommend maximum 15 upcoming events of user's interests by the order of relevance
    MAX_EVENTS = 15
    recommendation_events = []
    if "user_id" in session:
        user = crud.get_user_by_id(session["user_id"])
        print("\n" * 10, "Starting querying")
        # Querying based on user's address, interests, friends, date, favorite parks
        recommended = crud.recommend_events(user)
        # Sort recommended dictionary by (score, date) 
        sorted_recommendation = dict(sorted(recommended.items(), key=lambda item: (-item[1][0], item[1][1])))
        # From the dictionary, make a list of maximum 15 first event objects
        if len(sorted_recommendation) <= MAX_EVENTS:
            for key in sorted_recommendation.keys():
                print("key", key, "type of key", type(key))
                event = crud.get_event_by_id(key)
                recommendation_events.append(event)
        else:
            # Create new dict with 15 first key-value pairs
            limit_sorted_recommendation = dict(list(sorted_recommendation.items())[:15])
            print("15 sorted recommendation", limit_sorted_recommendation)
            for key in limit_sorted_recommendation.keys():
                event = crud.get_event_by_id(key)
                recommendation_events.append(event)
        print("\n" * 5)
        print(f"List of top events {recommendation_events}")
    
    return render_template("homepage.html", age_groups = AGE_GROUP, today = date.today(), recommendations = recommendation_events)

# Sign up page 
@app.route("/signup", methods =["GET", "POST"])
def sign_up():
    """ Get request renders the sign up page with the form in it, POST request processes the form"""

    # Using POST request, get input from the sign up form
    if request.method == "POST":
        fname = request.form.get("first").title()
        lname = request.form.get("last").title()
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
        # if user exists, flash message and restart sign up form
        flash("This email has already been used. Please try a different email.")
        return redirect("/signup")

    return render_template("signup.html")


# Login page
@app.route("/login", methods = ["GET", "POST"])
def login():
    """ GET request renders the login form, POST request processes the form """

    if "user_id" in session:
        flash("You are already logged in.")
        return redirect ("/")

    # Using POST method, get the input email and password from the log in form
    if request.method == "POST":
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
                return redirect("/")
            else: # if not, flash message
                flash("This email and password combination is incorrect.") 
        else:
            flash("This email and password combination is incorrect.") 
        
        return redirect("/login")

    return render_template("login.html")

# Render the form to reset password
@app.route("/forget_pw", methods = ["GET", "POST"])
def rest_password():
    """ GET request renders the reset password form, POST request processes the form"""

    # Using POST request, get input from the reset password form
    if request.method == "POST": 
        fname = request.form.get("first").title()
        lname = request.form.get("last").title()
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_pw = request.form.get("confirm_password")

        # Check if confirm password matches with password, if not, restart the form
        if password != confirm_pw:
            flash("Passwords don't match. Please try again.")
            return redirect("/reset_pw")

        # Check if name and email address match with a current user
        user = crud.get_user_by_name_email(fname, lname, email)
        if user:
            # Hash password for security reason
            user.password = argon2.hash(password)
            del password
            del confirm_pw
            db.session.commit()
            flash("Successfully reset your password. ")
            return redirect("/login")
        else:
            flash("Name and email addres do not match our record. Please try again or sign up for a new account.")
            return redirect("/forget_pw")

    return render_template("reset_password.html")


# Log out
@app.route("/logout")
def logout():
    """ Log out """

    if "user_id" in session:
        session.clear()
        flash("You were logged out. Come back soon!")
    
    return redirect("/")

# User profile
@app.route("/profile")
def show_profile():
    """ Show user profile """
    if "user_id" not in session:
        return redirect("/login")
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
    
    
# Render the complete profile page
@app.route("/complete_profile", methods = ["GET", "POST"])
def complete_profile():
    """ GET request renders the complete profile form, POST request updates user info in database"""

    user = crud.get_user_by_id(session["user_id"])
    # Post request, get info from the form and update database
    if request.method == "POST":
        home_address = request.form.get("address")
        home_lat = request.form.get("lat")
        home_lng = request.form.get("lng")
        activity_list = request.form.getlist("activity")

        # Process address to get the home state
        address_components = home_address.split(", ")
        home_state = re.search(r"[A-Z]{2}", address_components[2])
        # Update the address, state and coordinates to database
        user.home_address = home_address
        user.home_state = str(home_state.group())
        user.home_lat = home_lat
        user.home_lng = home_lng
        
        # Create user's favorite activity and add to database
        for one_activity in activity_list:
            activity = crud.get_activity_by_name(one_activity)
            if activity not in user.activities:
                user_like_activity = crud.create_user_favorite_activity(session["user_id"], activity.activity_id)
                db.session.add(user_like_activity)
        db.session.commit()
        return redirect("/profile")

    return render_template("complete_profile.html", age_groups = AGE_GROUP, activities=ACTIVITIES)


# Hosting an event
@app.route("/host", methods = ["GET", "POST"])
def host():
    """ GET request renders the host form, POST request processes the form"""

    if "user_id" not in session:
        flash("Please log in to host a playdate.")
        return redirect("/login")

    # Post request, get inputs from the form and create a new event
    if request.method == "POST":
        # Get host_id from session
        host_id = session["user_id"]
        # Get inputs from the form for event details
        title = request.form.get("title")
        description = request.form.get("description")
        name = request.form.get("location")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("zipcode")
        datemonth = request.form.get("date")
        start = request.form.get("start")
        end = request.form.get("end")
        age_group = request.form.get("age_group")
        standard_activities = request.form.getlist("activity")
        other_activity = request.form.get("otherActivity")
        # Duration for email reminder (on hosting form)
        reminder = request.form.get("reminder")

        # Query this input location to check it is already in database
        input_location = crud.get_location_by_name_and_address(name=name, address=address)
        # If not, create a new location object and add to database
        if not input_location:
            input_location = crud.create_new_location(name, address, city, zipcode, state)
            db.session.add(input_location)
            db.session.commit()

        # Check if this host already hosted an event on the same day, time and location
        event = crud.get_event_by_inputs(host_id, datemonth, start, end)
        if event:
            flash("You can't host two events at the same time.")
            return redirect ("/host")
        # Else, create a new event object and add to database
        new_event = crud.host_a_playdate(host_id, title, description, input_location.location_id,
                                    datemonth, start, end, age_group)
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

        flash(f"{new_event.host.fname}, your playdate {new_event.title} is scheduled on {new_event.date} from {new_event.start_time} to {new_event.end_time} at {new_event.location.name}.")
        flash("Congratulations! You will be an awesome host!")

        # If the host chooses to receive email reminder, collect info and store in a dictionary
        if reminder != "no":
            
            # Make dictionary 
            data = {}
            data["user"] = new_event.host.fname
            data["email"] = new_event.host.email
            data["title"] = new_event.title
            data["location"] = new_event.location.name
            data["start"] = new_event.start_time
            data["url"] = request.url_root
            if reminder == "1":
                # Calculate duration to schedule celery to send email
                duration = (new_event.date - timedelta(days=1) - date.today()).total_seconds()
                print("\n" * 5, "duration: ", duration)
                data["date"] = "tomorrow"
            else: 
                # Calculate duration to schedule celery to send email
                duration = (new_event.date - timedelta(days=2) - date.today()).total_seconds()
                print("\n" * 5, "duration: ", duration)
                data["date"] = "the day after tomorrow"
            print("\n" * 5, data["date"])
            # Schedule email
            send_reminder.apply_async(args=[data], countdown=duration)
            flash(f"Successfully scheduled email reminder to send {reminder} day(s) before your event.")

        return redirect("/profile")
    
    return render_template("hosting.html", today = date.today(), states=US_STATES, age_groups=AGE_GROUP, activities=ACTIVITIES)


# Update coordinates of location to database
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
    # Get event object 
    event_id = request.form.get("event_id")
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
            msg.html = f"We are sorry your playdate got canceled.<br> Please visit {homepage_url} to see other events."
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

    # Process lower case city_zipcode input
    if not city_zipcode.isdigit():
        city_zipcode = city_zipcode.title()

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
    print("event id", event_id)
    event = crud.get_event_by_id(event_id)
    
    # Check if this user_id already register for this event
    registered = False
    if "user_id" in session:
        registration = crud.get_registration(event_id, session["user_id"])
        if registration:
            registered = True
        
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

# Register for a playdate using AJAX request from REACT form
@app.route("/register", methods = ["POST"])
def register():
    """ Register user for an event with name and number of people """
    # Get inputs from the AJAX request
    name = request.get_json().get("name")
    num_people = int(request.get_json().get("num_people"))
    # For email reminder
    reminder = request.get_json().get("reminder")
    # Get user obj and event obj
    user_id = session["user_id"]
    user = crud.get_user_by_id(user_id)
    event_id = session["event_id"]
    event = crud.get_event_by_id(event_id)
    
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
    profile_url = f"<a href={url_root}/profile>your profile</a>"
    msg.html = f"{user.fname} {user.lname} has just registered to join your playdate {event.title}.<br> Visit {profile_url} to see more."
    mail.send(msg)

    # If the host chooses to receive email reminder, collect info and store in a dictionary
    if reminder != "no":
        # Make dictionary 
        data = {}
        data["user"] = registration.user.fname
        data["email"] = registration.user.email
        data["title"] = registration.event.title
        data["location"] = registration.event.location.name
        data["start"] = registration.event.start_time
        data["url"] = request.url_root
        # Calculate duration to schedule celery to send email 1 day before the event
        duration = (registration.event.date - timedelta(days=1) - date.today()).total_seconds()
        print("\n" * 5, "duration: ", duration)
        data["date"] = "tomorrow"
        
        # Schedule email
        send_reminder.apply_async(args=[data], countdown=duration)
        flash(f"Successfully scheduled email reminder to send {reminder} day(s) before your event.")
    
    return jsonify({"success": True, "registration": new_registration})


# Cancel an event registration
@app.route("/cancel_registration", methods=["POST"])
def cancel_registration():
    """ Cancel an event registration """
    # Get event_id from the form
    event_id = request.form.get("event_id")
    # Get the url root
    url_root = request.url_root
    # If this registration exists, delete it
    registration = crud.get_registration(event_id, session["user_id"])
    if registration:
        # Send email notification to the host about the cancelation
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
    # Check if user1 and user2 is the same
    if user1 == user2:
        return jsonify({"success": "self", "reason": "You can't follow yourself."})
    # Check if user1 and user2 are friends already
    if user1 in user2.get_all_friends():
        return jsonify({"success": False, "reason": "You already followed this host."})
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
    # Get user obj and event obj
    user_id = session["user_id"]
    user = crud.get_user_by_id(user_id)
    event_id = session["event_id"]
    event = crud.get_event_by_id(event_id)
    
    #Get inputs from the form
    recipients = request.args.getlist("friend")
    event_url = request.args.get("event_info")
    message_body = request.args.get("message")
    # Make the hyperlink by concatenating the root url and event url
    event_url = request.url_root + event_url 
    message_body += f"<br><a href='{event_url}'>{event.title}</a>"
    # Create an email notification and send
    msg = Message(f'{user.fname} {user.lname} recommends you check out this playdate', bcc=recipients)
    msg.html = message_body
    mail.send(msg)
    flash("You successfully sent invitations to this playdate.")
    return redirect("/profile")


# Route to add parks to favorites
@app.route("/like_park")
def like_park():
    """ Add parks to favorite and update in the database """

    location_id = request.args.get("location_id")
    location = crud.get_location_by_id(location_id)
    user = crud. get_user_by_id(session["user_id"])
    # Check if user has already liked this park 
    if location in user.locations:
        return jsonify({"success": False})
    # Create and update user like park to database
    user_like_park = crud.create_user_favorite_park(session["user_id"], location_id)
    db.session.add(user_like_park)
    db.session.commit()
    
    return jsonify({"success": True})


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
    
    return render_template("calendar.html", cal_events=events_dict, today = date.today())

# Send reminder email
@celery.task
def send_reminder(data):
    """ Function to send email reminders """
    with app.app_context():
        msg = Message("You have an upcoming playdate tomorrow", recipients=[data["email"]])
        msg.html = f"{data['user']}, are you excited about your upcoming playdate?<br> You don't need to wait long, your playdate at {data['location']} at {data['start']} is {data['date']}! <br> Log in to <a href={data['url']}/profile>your profile</a> to see details."
        mail.send(msg)

if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)