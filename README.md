# Project Playdate Birdies

A web app where parents and grandparents can find playdates for their children.

## About

- Playdate Birdies is a community of parents and grandparents who love to bring their kids to outdoor activities to learn, play and make friends.
- No matter how young children are, outdoor activities are beneficial to their development.
- Interacting with other kids of similar age helps them socialize and have fun.
- Parents can volunteer to host a playdate at their chosen location (usually a public park). Other parents can search for a playdate of their interest and register to join.
- The app supports other features, such as following hosts, send email invitations to friends, add events to personal calendar, receive email reminders, and suggest playdates based on users' interests.
- Let's help our kids play, grow and make friends, one playdate at a time.

## Technologies Used

- Back-end: Python (Flask, SQLAlchemy, Flask-Mail, Celery)
- Database: SQL, PostgreSQL, SQLAlchemy
- Front-end: Javascript, HTML, Bootstrap, AJAX, JSON, Jinja, React
- APIs: Google Map APIs (Maps JavaScript API, Places API, Geolocation API)

## Features

- Create user account, login and logout
- User profile page with event calendar and receive email reminders of upcoming events
- Hosting feature, with the help of address autocompletion, and includes activity recommendations based on age group (to be implemented)
- Searching by city or zipcode, date, age group, and activities
- Search results show playdate details with location markers on the map as well as user's location (if granted permission)
- Register feature and check out who's coming to the playdate
- Cancel playdates or registrations with email notifications to the host/participants
- Follow hosts, and send email invitations to friends
- Personalize playdate suggestions based on users' interests 


## Set Up

To run this project, install it locally:

- Clone this repository
$ git clone https://github.com/hoaian-phan/project-playdate-birdies.git

- Go into the repository
$ cd project-playdate-birdies

- Install dependencies
$ pip3 install -r requirements.txt

- Run the app
$ python3 server.py


## Project Status: 
Project is in progress. Features are now completed. Starting on tests and styling.
