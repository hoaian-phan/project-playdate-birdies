""" CRUD operations """

from model import (db, connect_to_db, User, Event, Registration, Location,
                   Activity, ActivityAssociation, UserLikeActivity, UserLikePark) 
from datetime import date, timedelta
from geopy import distance


today = date.today()
# Sign up
def sign_up(first, last, email, password):
    """ Create and return a new user """

    user = User(fname=first, lname=last, email=email, password=password)

    return user

# Sign up with homestate for seed database
def sign_up_with_homestate(first, last, email, password, home_state):
    """ Create and return a new user """

    user = User(fname=first, lname=last, email=email, password=password, home_state=home_state)

    return user

# Log in: Get user by email
def get_user_by_email(email):
    """ Return user object of the input email """

    user = User.query.filter_by(email=email).first()

    return user

# User: Get user by user_id
def get_user_by_id(user_id):
    """ Return user object by id """

    user = User.query.get(user_id)

    return user

# User: Get user by name and email
def get_user_by_name_email(fname, lname, email):
    """ Return a user with the input name and email """

    user = User.query.filter_by(fname=fname, lname=lname, email=email).first()

    return user



# User: Get a list of users that have events tomorrow
def get_users_of_tomorrow_events(day):
    """ Return a list of users who have events tomorrow"""

    hosts = User.query.join(Event).filter(Event.date - day == 2).all()
    attendants = User.query.join(Registration).join(Event).filter(Event.date - day == 1).all()

    return hosts + attendants

# Location: Get location by name and adress
def get_location_by_name_and_address(name, address):
    """ Return location object of the input name and address"""

    location = Location.query.filter_by(name=name, address=address).first()

    return location

# Location: Create a new location without coordinates
def create_new_location_no_coords(name, address, city, zipcode, state):
    """ Create and return a location object """

    location = Location(name=name, address=address, city=city, zipcode=zipcode, state=state)

    return location

# Location: Create a new location
def create_new_location(name, address, city, zipcode, state, lat, lng, photo):
    """ Create and return a location object """

    location = Location(name=name, address=address, city=city, zipcode=zipcode, state=state, lat=lat, lng=lng, photo=photo)

    return location

# Location: Get a location object by id
def get_location_by_id(location_id):
    """ Return a location object by its id """

    location = Location.query.get(location_id)

    return location

# Event: Create a new event
def host_a_playdate(host_id, title, description, location_id, date, start, end, age_group):
    """ Create and return an event object"""

    event = Event(host_id=host_id, title=title, description=description, location_id=location_id, 
                  date=date, start_time=start, end_time=end, age_group=age_group)

    return event


# Event: Return a list of event objects by inputs
def get_events_by_inputs(city_zipcode, date, age_group, activity):
    """ Return an event object by input parameters"""

    events = db.session.query(Event).join(Location)

    if date:
        events = events.filter(Event.date==date)
    else:
        events = events.filter(Event.date > today)
    if age_group and age_group != 'any age':
        events = events.filter(Event.age_group==age_group)
    if city_zipcode:
        events = events.filter((Location.zipcode==city_zipcode) | (Location.city==city_zipcode))
    if activity:
        events = events.join(ActivityAssociation).join(Activity)
        events = events.filter((Activity.name.like(f"%{activity}%")))
    
    return events.all()


# Event: Get event by event id
def get_event_by_id(event_id):
    """ Return an event object by its id"""

    event = Event.query.get(event_id)

    return event

# Event: Get event by inputs
def get_event_by_inputs(host_id, event_date, start):
    """ Return an event by inputs"""

    event = Event.query.filter_by(host_id=host_id, date=event_date, start_time=start).first()

    return event


# Event: Get a list of events this user has registered for
def get_events_by_userid(user_id):
    """ Return a list of events this user has registered for"""

    events = Event.query.join(Registration).filter(Registration.user_id==user_id).all()

    return events

# Event: Get a list of events which are scheduled for tomorrow
def get_tomorrow_events(day):
    """ Return a list of events which are scheduled for tomorrow"""

    events = Event.query.filter(Event.date - day == 1).all()

    return events


# Categorize pass and future events:
def is_future(event):
    """ Return true if the input event date is in the future """

    # Compare event date to today
    if event.date > today:
        return True
    return False

# Recommended upcoming events:
def recommend_events(user):
    """ Return a list of recommended upcoming events sorted by score"""

    # Create a dictionary with key is the event and value is the scores
    recommended = {}
    
    # Get all upcoming events within the next 15 days in user's home state
    events = db.session.query(Event).join(Location)
    events = events.filter(Event.date - today < 15, Event.date - today > 0)
    events = events.filter(Location.state == user.home_state)
    events = events.options(db.joinedload('location'), db.joinedload('activities'), db.joinedload('host')).all()
    
    user_home = (user.home_lat, user.home_lng)
    
    # Give each event a score based on scoring criteria
    for event in events:
        print("\n"* 2, "Starting scoring")
        # Using geopy distance to calculate distance between home and parks, if over 25 miles, skip it
        event_coords = (event.location.lat, event.location.lng)
        distance_from_home = distance.distance(user_home, event_coords).miles
        if distance_from_home > 25:
            continue
        # Initialize score
        score = 0
        # If host is a friend -> +10 points
        if event.host in user.get_all_friends():
            score += 10
        # If location is in favorite parks -> +10 points
        if event.location in user.locations:
            score += 9
        # otherwise, if location is within 10 miles from home -> +6 points
        elif distance_from_home < 10:
            score += 6
        # If event has at least one interested activity -> +8 points
        for activity in event.activities:
            if activity in user.activities:
                score += 8
                break
        # If event is within the next 7 days -> +7 points
        if event.date - today < timedelta(days=7):
            score += 7
    
        # Add event and its score to dict
        recommended[f"{event.event_id}"] = (score, event.date)

    return recommended


# Registration: Get registration by event id and user id
def get_registration(event_id, user_id):
    """ Return registration object by event id and user id"""

    registration = Registration.query.filter_by(event_id=event_id, user_id=user_id).first()

    return registration

# Registration: Create a new registration
def create_new_registration(event_id, user_id, num_people = 1):
    """ Create and return a new registration """

    registration = Registration(event_id=event_id, user_id=user_id, num_people=num_people)

    return registration

# Registration: Delete all registrations
def delete_registrations(event_id):
    """ Delete registrations associated with this input event_id """

    Registration.query.filter(Registration.event_id==event_id).delete()


# Activity: Get an activity object by its name
def get_activity_by_name(activity_name):
    """ Return an activity object by its name """

    activity = Activity.query.filter_by(name=activity_name).first()

    return activity

# Activity: Create an activity
def create_an_activity(activity):
    """ Create and return an activity object """

    activity = Activity(name=activity)

    return activity

# Activity association: Create an activity associated with an event
def create_activity_event_asso(activity_id, event_id):
    """ Create and return an activity-event association object """

    activity_event = ActivityAssociation(activity_id=activity_id, event_id=event_id)

    return activity_event

# Activity association: Delete an activity association object with an event_id
def delete_activity_event_asso(event_id):
    """ Delete an activity association object associated with input event_id"""

    ActivityAssociation.query.filter(ActivityAssociation.event_id==event_id).delete()

# User like activity: Create
def create_user_favorite_activity(user_id, activity_id):
    """ Create and return user's favorite activity"""

    user_like_activity = UserLikeActivity(user_id=user_id, activity_id=activity_id)

    return user_like_activity


# User like park
def create_user_favorite_park(user_id, location_id):
    """ Create and return user's favorite park"""

    user_like_park = UserLikePark(user_id=user_id, location_id=location_id)

    return user_like_park


