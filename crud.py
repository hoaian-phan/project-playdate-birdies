""" CRUD operations """

from model import (db, connect_to_db, User, Event, Registration, Location,
                   Activity, Equipment, ActivityAssociation) # UserAssociation



# Sign up
def sign_up(first, last, email, password):
    """ Creae an account """

    user = User(fname=first, lname=last, email=email, password=password)

    return user

# Log in: Get user by email
def get_user_by_email(email):
    """ Return user object of the input email """

    user = User.query.filter_by(email=email).first()

    return user


