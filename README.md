# Project Playdate Birdies

A web app where parents and grandparents can find playdates for their children.

## About

- Playdate Birdies is a community of parents and grandparents who love to bring their kids to outdoor activities to learn, play and make friends.
- No matter how young children are, outdoor activities are beneficial to their development.
- Interacting with other kids of similar age helps them socialize and have fun.
- Parents can volunteer to host a playdate at their chosen location (usually a public park). Other parents can search for a playdate of their interest and register to join.
- The app supports other features, such as following hosts, send email invitations to friends, add events to personal calendar, receive email reminders, and suggest playdates based on users' interests.
- Let's help our kids play, grow and make friends, one playdate at a time.
<p align="center">
  <img src="static/image/Readme/homepage - fullscreen.png" width=800>
 </p>
 <p align="center">
  <img src="static/image/Readme/hp-hosting.png" width=800>
 </p>
 

## Technologies Used

- Back-end: Python (Flask, SQLAlchemy, Flask-Mail, Celery)
- Database: SQL, PostgreSQL, SQLAlchemy
- Front-end: Javascript, HTML, Bootstrap, AJAX, JSON, Jinja, React
- APIs: Google Map APIs (Maps JavaScript API, Places API, Geolocation API)

## Features

- Users can create an account, login, reset password and logout. Users' data is saved in the database with password being hashed by Python library passlib, argon2 for security.
<p align="center">          
  <img src="static/image/Readme/signup-login-resetpw.png" width=800>
</p>

- Users can perform a search for a playdate by one or multiple parameters such as city or zipcode, date, age group, and/or activities. This searching feature is implemented by query chains in SQLAlchemy to the PostgreSQL database.
<p align="center">          
  <img src="static/image/Readme/homepage - small_screen.png" width=400>
</p>

- Search results show playdate details with location markers on the map as well as user's location (if granted permission). I implemented this page using Google Maps APIs to display map, location markers and user's location. Result details are shown by DOM manipulation in JavaScript.
<p align="center">          
  <img src="static/image/Readme/search_results.png" width=800>
</p>

- Register feature: REACT page with updates of who's coming to the playdate and option to receive email reminder. Email feature was implemented by Flask-Mail and reminders are scheduled using Celery.
<p align="center">          
  <img src="static/image/Readme/register.png" width=800>
</p>                                                    

- Hosting feature, with the help of address autocompletion in Google Map APIs.
<p align="center">          
  <img src="static/image/Readme/host.png" width=800>
</p>

- User profile with contact info, favorite and events as list. Users can update profile or change their password anytime.
<p align="center">          
  <img src="static/image/Readme/profile.png" width=800>
</p>

- Users can view their playdates in calender. I implemented this calendar by using FullCalendar in JavaScript.
<p align="center">          
  <img src="static/image/Readme/calendar.png" width=800>
</p>

- Follow hosts, add park to favorites, cancel playdates or registrations with email notifications to the host/participants. All changes are updated in the database.
<p align="center">          
  <img src="static/image/Readme/follow.png" width=500>
</p>

- Send email invitations to friends. An email with the event registration link will be sent to selected friends and they can register if interested.
<p align="center">          
  <img src="static/image/Readme/invite.png" width=800>
</p>

- Personalize playdate suggestions based on users' interests. A list of recommended playdates sorted by score and date is displayed on the homepage for logged in users to browse.
<p align="center">          
  <img src="static/image/Readme/recommend.png" width=800>
</p>

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
