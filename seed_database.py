""" Script to seed database """

import os
import json
from random import choice
from datetime import datetime

import crud
import model
import server

os.system("dropdb playdates")
os.system("createdb playdates")

model.connect_to_db(server.app)
model.db.create_all()

AGE_GROUP = ["infants", "toddlers", "preschoolers", "kindergarteners",
            "elementary", "middleschool", "highschool", "any age"]

DATES = ['2022-03-20', '2022-03-19', '2022-03-27', '2022-03-26']

date_objs = []
for date in DATES:
    date = datetime.strptime(date, '%Y-%m-%d').date()
    date_objs.append(date)

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

    locations_in_db.append(crud.create_new_location(name, address, city, zipcode, state))

model.db.session.add_all(locations_in_db)
model.db.session.commit()

# Create 10 users
FIRST_NAME = ["Emma", "Amelia", "Ava", "Olivia", "Luna", "Mia", "Sophia", "Charlotte", "Isabella", "Ella"]
LAST_NAME = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

for n in range(10):
    fname = FIRST_NAME[n]
    lname = LAST_NAME[n]
    email = f'user{n}@test.com'
    password = '12345'

    user = crud.sign_up(fname, lname, email, password)
    model.db.session.add(user)
    model.db.session.commit()

    # Create 100 events
    for i in range (10):
        host_id = user.user_id
        title = f'playdate {i} of {n}'
        description = 'Have fun and make friends'
        location_id = choice(locations_in_db).location_id
        # location_id = model.Location.location_id
        date = choice(date_objs)
        start_time = '11:00:00'
        end_time = '15:00:00'
        age_group = choice(AGE_GROUP)

        event = crud.host_a_playdate(host_id, title, description, location_id, date, start_time, end_time, age_group)
        model.db.session.add(event)

model.db.session.commit()

