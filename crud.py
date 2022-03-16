""" CRUD operations """

from model import (db, connect_to_db, User, Event, Registration, Location,
                   Activity, Equipment, ActivityAssociation) # UserAssociation



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

# Location: Create a new location
def create_new_location(name, address, city, zipcode, state):
    """ Create and return a location object """

    location = Location(name=name, address=address, city=city, zipcode=zipcode, state=state)

    return location

# Event: Create a new event
def host_a_playdate(host_id, title, description, location_id, date, start, end, age_group):
    """ Create and return an event object"""

    event = Event(host_id=host_id, title=title, description=description, location_id=location_id, 
                  date=date, start_time=start, end_time=end, age_group=age_group)

    return event
