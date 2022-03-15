""" Server for playdate birdies apps """

from flask import (Flask, render_template, request, redirect, flash, session)
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "giahoa"
app.jinja_env.undefined = StrictUndefined

# 1. Homepage route
@app.route("/")
def homepage():
    """ Display homepage """

    return render_template("homepage.html")

# 2a. Sign up page with GET to render template with the sign up form
@app.route("/signup")
def sign_up():
    """ Render the sign up page with the form in it"""

    return render_template("signup.html")


# 2b. Create an account route
@app.route("/signup", methods = ["POST"])
def create_user():
    """ Create a new user """
    # Using POST request, get input from the sign up form
    fname = request.form.get("first")
    lname = request.form.get("last")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_pw = request.form.get("confirm_password")

    # Check if confirm password matches with password, if not, restart the sign up form
    # Use Javascript to add event handler and prevent submitting the form
    if password != confirm_pw:
        flash("Passwords don't match. Please try again.")
        return redirect("/signup")

    # Otherwise, get user object by the input email
    user = crud.get_user_by_email(email)

    # If this user doesn't exist in database, create and add this new user to database
    if not user:
        new_user = crud.sign_up(fname, lname, email, password)
        db.session.add(new_user)
        db.session.commit()
        # Flash message and add user_id to session 
        flash("Successfully created an account.")
        session["user_id"] = new_user.user_id 
        # return user to their previous page (hosting or register or homepage) - add later
        return redirect("/")
    else: # if user exists, flash message and restart sign up form
        flash("This email has already been used. Please try a different email.")
        return redirect("/signup")



# 3. Login with GET to render template login with the login form
@app.route("/login")
def login_get():
    """ Render the login page with the form in it"""

    return render_template("login.html")

# 4. Login route
@app.route("/login", methods = ["POST"])
def login():
    """ User login """

    # Using POST method, get the input email and password from the log in form
    email = request.form.get("email")
    password = request.form.get("password")
    # remember = request.form.get("remember_me")

    # Get the user object by input email
    user = crud.get_user_by_email(email)

    # If this user exists in database, check if password matches; if yes, log in
    if user:
        if password == user.password:
            flash("Log in successfully.")
            session["user_id"] = user.user_id
            # return user to their previous page (hosting or register or homepage) - add later
            return redirect("/")
        else: # if not, flash message
            flash("This email and password combination is incorrect.") #or click Forget password
    else:
        flash("This email and password combination is incorrect.") #or click Forget email address
    
    return redirect("/login")




# 4. Search results


# 5. Hosting



if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)