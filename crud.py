""" CRUD operations """

from model import (db, connect_to_db, User, Event, Registration, Location,
                   Activity, Equipment, ActivityAssociation) # UserAssociation
from datetime import date



# Sign up
def sign_up(first, last, email, password):
    """ Create and return a new user """

    user = User(fname=first, lname=last, email=email, password=password)

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

# Location: Get location by name and adress
def get_location_by_name_and_address(name, address):
    """ Return location object of the input name and address"""

    location = Location.query.filter_by(name=name, address=address).first()

    return location

# Location: Create a new location
def create_new_location(name, address, city, zipcode, state):
    """ Create and return a location object """

    location = Location(name=name, address=address, city=city, zipcode=zipcode, state=state)

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
    if age_group and age_group != 'any age':
        events = events.filter(Event.age_group==age_group)
    if city_zipcode:
        events = events.filter((Location.zipcode==city_zipcode) | (Location.city==city_zipcode))
    if activity:
        events = events.join(ActivityAssociation).join(Activity)
        # for activity in activities:
        events = events.filter((Activity.name.like(f"%{activity}%")))
    
    return events.all()


# Event: Get event by event id
def get_event_by_id(event_id):
    """ Return an event object by its id"""

    event = Event.query.get(event_id)

    return event

# Categorize pass and future events:
def is_future(event):
    """ Return true if the input event date is in the future """
    # Get today's date
    today = date.today()
    # Compare event date to today
    if event.date > today:
        return True
    return False

# Registration: Get registration by event id and user id
def get_registration(event_id, user_id):
    """ Return registration object by event id and user id"""

    registration = Registration.query.filter_by(event_id=event_id, user_id=user_id).first()

    return registration

# Registration: Create a new registration
def create_new_registration(event_id, user_id):
    """ Create and return a new registration """

    registration = Registration(event_id=event_id, user_id=user_id)

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
