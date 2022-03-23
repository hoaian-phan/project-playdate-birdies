""" Server for playdate birdies apps """

from flask import (Flask, render_template, request, redirect, flash, session, jsonify)
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "giahoa"
app.jinja_env.undefined = StrictUndefined

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

    # If this user doesn't exist in database, create and add this new user to database
    if not user:
        new_user = crud.sign_up(fname, lname, email, password)
        db.session.add(new_user)
        db.session.commit()
        # Flash message and add user_id to session 
        flash(f"Hi {new_user.fname}, welcome to Playdate Birdies community.")
        session["user_id"] = new_user.user_id 
        session["user_fname"] = new_user.fname
        if "event_id" in session:
            event = crud.get_event_by_id(session["event_id"])
            return render_template("confirm.html", event=event)
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
        if password == user.password:
            flash(f"Hi {user.fname}, welcome back.")
            session["user_id"] = user.user_id
            session["user_fname"] = user.fname
            if "event_id" in session:
                event = crud.get_event_by_id(session["event_id"])
                return render_template("confirm.html", event=event)
            # return user to their previous page (hosting or register or homepage) - add later
            return redirect("/")
        else: # if not, flash message
            flash("This email and password combination is incorrect.") #or click Forget password
    else:
        flash("This email and password combination is incorrect.") #or click Forget email address
    
    return redirect("/login")

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

    flash(f"{new_event.host.fname}, your playdate {new_event.title} is scheduled on {new_event.date} from {new_event.start_time} to {new_event.end_time} at {new_event.location.name}.")
    flash("Congratulations! You will be an awesome host!")
    
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

# # Search by activity
# @app.route("/search_activity")
# def serach_by_activity():
#     """ Search by activity"""
#     activity = request.args.get("activity")
#     events = crud.get_events_by_activity(activity=activity)
#     return render_template("register.html", events=events)

# 6. Display event details
@app.route("/events")
def show_details():
    """ Show event details """

    # Get the event_id from fetch call
    event_id = request.args.get("event_id")

    # Get the event by event_id
    event = crud.get_event_by_id(event_id)
    print(event.activities)
    print(type(event.activities))

    

    # Remake event dictionary for jsonify
    event = {
        "event_id": event.event_id,
        "host": event.host.fname + " " + event.host.lname,
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
        "activity_list": [activity.name for activity in event.activities]
        #event.activities[0].name, event.activities[1].name, event.activities[2].name]
    }

    return jsonify(event)

# 6b. Update coordinates of location to database
@app.route("/update_coordinates", methods = ["POST"])
def update_coordinates():
    """ Update the location coordinates in the database """
    # Get info from the fetch call
    lat = request.json.get("lat")
    lng = request.json.get("lng")
    location_id = request.json.get("location_id")

    # Get the location object
    location = crud.get_location_by_id(location_id)
    # Update the coordinates
    location.lat = lat
    location.lng = lng
    db.session.commit()

    return {"status": "ok"}


# 7a. Register for a playdate
@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register for a playdate """
    #  If POST method
    if request.method == "POST":
        # Get event_id from the form
        event_id = request.form.get("event_id")

        # If user is not logged in, return to login page
        if "user_id" not in session:
            flash("Please log in to register")
            session["event_id"] = event_id
            return redirect("/login")
    else: # If GET method
        event_id = session["event_id"]

    # Get user_id from session
    user_id = session["user_id"]

    # Get the registration by this user_id and event_id
    registration = crud.get_registration(event_id, user_id)
    # Check if this user has already registered for this event
    if registration:
        flash("You have already registered for this playdate.")
        # will return to user profile to see list of future events
        return redirect("/")
    else:
        registration = crud.create_new_registration(event_id, user_id)
        db.session.add(registration)
        db.session.commit()

    return render_template("confirm_registration.html", registration=registration)

# 7c. Confirm registration after user log in
@app.route("/confirm")
def confirm():
    """ After user logs in, ask for confirmation before registering for the event """

    answer = request.args.get("confirm")
    if answer == "yes":
        return redirect("/register")
    else:
        if "event_id" in session:
            del session["event_id"]
            return redirect("/")


if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)