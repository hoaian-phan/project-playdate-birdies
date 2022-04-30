""" Script to seed database """

import os
import json
from random import choice, sample, choices
from datetime import datetime, date, timedelta

import crud
import model
import server

os.system("dropdb playdates")
os.system("createdb playdates")

model.connect_to_db(server.app)
model.db.create_all()

AGE_GROUP = ["infants", "toddlers", "preschoolers", "kindergarteners",
            "elementary", "middleschool", "highschool", "any age"]

ACTIVITIES = ["Draw with chalk", "Go on a scavenger hunt", "Kick a ball", "Blow bubbles",
            "Play tag", "Tug of war", "Fly a kite", "Squirt water guns", "Basket ball", 
            "Play with sand", "Have a race", "Make paper airplanes", "Water balloon t-ball",
            "Hula hoop", "Drawing and coloring", "Collect leaves", "Jumping rope", "Bag jumping", 
            "Bike/scooter riding", "Volley ball", "Obstacle course", "Finger painting", "Singing",
            "Music time", "Dancing", "Musical chair"]

TITLE = ["Easter egg hunt", "Spring break playdate", "Wonderful outdoor games", "Hey friends, let's play",
        "Explore nature", "Fun day at the park", "Mommy and me playdate", "Spring time", "Ball games",
        "Play and make friends", "Friendship", "Let's have fun", "Hi, nice to meet you"]

# Create 10 random dates
# initializing dates ranges 
test_date1, test_date2 = date(2022, 4, 1), date(2022, 5, 30)
  
# printing dates 
print("The original range : " + str(test_date1) + " " + str(test_date2))
  
# initializing K
K = 10
  
res_dates = [test_date1]
  
# loop to get each date till end date
while test_date1 != test_date2:
    test_date1 += timedelta(days=1)
    res_dates.append(test_date1)

# random K dates from pack
res = choices(res_dates, k=K)

date_objs = []
for date in res:
    date_objs.append(date)
    print("The date is ", date)

# Create 10 locations
with open('data/parks.json') as f:
    park_data = json.loads(f.read())

locations_in_db = []
for park in park_data:
    name = park['name']
    address = park['address']
    city = park['city']
    zipcode = park['zipcode']
    state = park['state']
    lat = park['lat']
    lng = park['lng']
    photo = park['photo']

    locations_in_db.append(crud.create_new_location(name, address, city, zipcode, state, lat, lng, photo))

model.db.session.add_all(locations_in_db)
model.db.session.commit()

# Create activities
for j, game in enumerate(ACTIVITIES):
    activity = crud.create_an_activity(game)
    model.db.session.add(activity)
    model.db.session.commit()

# Create 10 users
FIRST_NAME = ["Emma", "Amelia", "Ava", "Olivia", "Luna", "Mia", "Sophia", "Charlotte", "Isabella", "Ella"]
LAST_NAME = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

for n in range(10):
    fname = FIRST_NAME[n]
    lname = LAST_NAME[n]
    email = f'user{n}@test.com'
    password = '12345'
    home_state = 'CA'

    user = crud.sign_up_with_homestate(fname, lname, email, password, home_state)
    model.db.session.add(user)
    model.db.session.commit()

    # Create 100 events
    for i in range (10):
        host_id = user.user_id
        title = choice(TITLE)
        description = None
        location_id = choice(locations_in_db).location_id
        date = choice(date_objs)
        start_time = choice(['10:00:00 AM', '11:00:00 AM', '12:00:00 PM', '1:00:00 PM', '2:00:00 PM'])
        end_time = choice(['3:00:00 PM', '4:00:00 PM', '5:00:00 PM'])
        age_group = choice(AGE_GROUP)

        event = crud.host_a_playdate(host_id, title, description, location_id, date, start_time, end_time, age_group)
        model.db.session.add(event)
        model.db.session.commit()

        for k in range(3):
            activity_event = crud.create_activity_event_asso(choice(range(1, 27)), event.event_id)
            model.db.session.add(activity_event)
            model.db.session.commit()

for m in range(100):
    registration = crud.create_new_registration(choice(range(1, 101)), choice(range(1, 10)), choice(range(1,5)))
    model.db.session.add(registration)
    model.db.session.commit()




