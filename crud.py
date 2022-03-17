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

# # Location: Get a list of location by city or zipcode
# def get_locations_by_city_or_zipcode(city=None, zipcode=None):
#     """ Return a list of location object by input city or zipcode"""

#     locations = Location.query.filter(db.or_(Location.city==city, Location.zipcode==zipcode)).all()

#     return locations

# Event: Create a new event
def host_a_playdate(host_id, title, description, location_id, date, start, end, age_group):
    """ Create and return an event object"""

    event = Event(host_id=host_id, title=title, description=description, location_id=location_id, 
                  date=date, start_time=start, end_time=end, age_group=age_group)

    return event


# Event: Return a list of event objects by inputs
def get_events_by_inputs(city_zipcode, date, age_group):
    """ Return an event object by input parameters"""

    events = db.session.query(Event).join(Location)
    if date:
        events = events.filter(Event.date==date)
    if age_group and age_group != 'any age':
        events = events.filter(Event.age_group==age_group)
    if city_zipcode:
        events = events.filter((Location.zipcode==city_zipcode) | (Location.city==city_zipcode))

    return events.all()

