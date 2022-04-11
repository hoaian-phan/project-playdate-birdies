""" Models for playdate birdie apps """

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table between users. It defines a many-to-many relationship between 2 users (friends).
friend = db.Table(
    'friends',
    db.Column('friend_id', db.Integer, primary_key=True),
    db.Column('f1_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('f2_id', db.Integer, db.ForeignKey('users.user_id'))
)


# 1. User class
class User(db.Model):
    """ User information """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    home_address = db.Column(db.String)
    home_state = db.Column(db.String(2))
    home_lat = db.Column(db.Float)
    home_lng = db.Column(db.Float)


    events = db.relationship("Event", back_populates="host")
    registrations = db.relationship("Registration", back_populates="user")
    # Following other users
    following = db.relationship("User", secondary=friend,
                                primaryjoin=user_id == friend.c.f1_id,
                                secondaryjoin=user_id == friend.c.f2_id,
                                backref='followers')
    # followers: those following you
    locations = db.relationship("Location", secondary="user_like_park", back_populates="users")
    activities = db.relationship("Activity", secondary="user_like_activity", back_populates="users")

    def get_all_friends(self):
        """ Get all friends, those you are following AND those following you. """
        return self.following + self.followers

    def __repr__(self):
        """ Display user object on the screen """

        return f"<User user_id={self.user_id} name={self.fname} {self.lname}>"



# 2. Event class
class Event(db.Model):
    """ A playdate information """

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    age_group = db.Column(db.String) # drop down 

    host = db.relationship("User", back_populates="events") 
    location = db.relationship("Location", back_populates="events")
    registrations = db.relationship("Registration", back_populates="event")
    activities = db.relationship("Activity", secondary="activity_association", back_populates="events")


    def __repr__(self):
        """ Display event object on the screen """

        return f"<Event event_id={self.event_id} title={self.title}>"

# 3. Registration class
class Registration(db.Model):
    """ A user registration for an event """

    __tablename__ = "registrations"

    regist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    num_people = db.Column(db.Integer)
    
    event = db.relationship("Event", back_populates="registrations")
    user = db.relationship("User", back_populates="registrations")

    def __repr__(self):
        """ Display a registration object on the screen"""

        return f"<Registration regist_id={self.regist_id} event_id={self.event_id} user_id={self.user_id}>"


# 4. Location class
class Location(db.Model):
    """ A location information """

    __tablename__ = "locations"

    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    zipcode = db.Column(db.String, nullable=False)
    state = db.Column(db.String(2), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    photo = db.Column(db.String) # url

    events = db.relationship("Event", back_populates="location")
    users = db.relationship("User", secondary="user_like_park", back_populates="locations")

    def __repr__(self):
        """ Display location object on the screen"""

        return f"<Location location_id={self.location_id} name={self.name}>"

# 5. Activity class
class Activity(db.Model):
    """ An activity """

    __tablename__ = "activities"

    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)

    events = db.relationship("Event", secondary="activity_association", back_populates="activities")
    users = db.relationship("User", secondary="user_like_activity", back_populates="activities")

    def __repr__(self):
        """ Display an activity object on the screen"""

        return f"<Activity activity_id={self.activity_id} name={self.name}>"

# 6. Activity association class
class ActivityAssociation(db.Model):
    """ An activity - event association """

    __tablename__ = "activity_association"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.activity_id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"), nullable=False)

    def __repr__(self):
        """ Display activity association on the screen"""

        return f"<ActivityAssociation id={self.id} activity_id={self.activity_id} event_id={self.event_id}>"


# User's interests (Association table)
class UserLikeActivity(db.Model):
    """ User's interests"""

    __tablename__ = "user_like_activity"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.activity_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """ Display user's interests on the screen"""

        return f"<UserLikeActivity id={self.id} user_id={self.user_id} activity_id={self.activity_id}>"


# User's interests (Association table)
class UserLikePark(db.Model):
    """ User's interests"""

    __tablename__ = "user_like_park"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """ Display user's interests on the screen"""

        return f"<UserLikePark id={self.id} user_id={self.user_id} location_id={self.location_id}>"

# Connect to database
def connect_to_db(flask_app, db_uri="postgresql:///testdb", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


# Create example data for testing
def example_data():
    """ Create example data for the test database"""

    user_1 = User(fname="Rhena", lname="Fanun", email="rhena@hb.com", password="12345")
    user_2 = User(fname="Abriel", lname="Fanun", email="abriel@hb.com", password="12345")
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.commit()

    location_1 = Location( name="Greenwood Park", address="24016 Eden Ave", city="Hayward", zipcode= "94541", state="CA")
    db.session.add(location_1)
    db.session.commit()

    event_1 = Event(host_id= user_1.user_id, title = "playdate of", description = 'Have fun and make friends', location_id = "01",
                    date = "2022-03-27", start_time = '11:00:00', end_time = '15:00:00', age_group = "any age")
    db.session.add(event_1)
    db.session.commit()

if __name__ == "__main__":
    from server import app

    connect_to_db(app)