from flask import Flask, redirect, render_template, url_for, abort, session
from flask_dance.consumer import OAuth2ConsumerBlueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from aux.logs import log2term
import db

import os

app = Flask(__name__)

######################## OAUTH ########################
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = "asintisfun"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example",
    __name__,
    client_id="1132965128044796",
    client_secret=
    "HwdRWx6wP7rJkb2UKmxbVoYkjrok4xD/tDlcwom+0qnJLDMrwT3aavKo9OXaQC5gMc+uy7CfbcU6XJL6qASy+w==",
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)
app.register_blueprint(fenix_blueprint)


######################## FLASK ########################
@app.route("/API/<string:username>/videos/", methods=['GET'])
def UserVideos(username):
    user_videos = []
    other_users_videos = []

    my_videos = db.GetUserVideos(username)
    other_videos = db.GetOtherUsersVideos(username)

    if(my_videos == None):
        log2term('W', f'There were no videos found for user {username}')
    else:    
        for video in my_videos:
            video_dict = video.to_dictionary()
            user_videos.append(video_dict) # This is a list

    # Create a list with all of the videos from other users
    if(other_videos == None):
        log2term('W', f'There were no videos found for other users ({username})')
    else:   
        for video in other_videos:
            video_dict = video.to_dictionary()
            other_users_videos.append(video_dict) # This is a list

    return {'user_videos': user_videos, "other_users_videos": other_users_videos} # A dict must be returned
        


@app.route("/")
def Index():
    return render_template("welcome.html",
                           logged_in=fenix_blueprint.session.authorized)


@app.route("/dashboard")
def Dashboard():
    # Check if user is loggen in
    if fenix_blueprint.session.authorized == False:
        return redirect(url_for("fenix-example.login"))
    else:
        try:
            user_data = (
                fenix_blueprint.session.get("/api/fenix/v1/person/")).json()
        except TokenExpiredError as e:
            log2term('E', f'{e.__class__.__name__}. Logging out...')
            return redirect(url_for("LogOut"))

        # Extract user information
        username = user_data['username']
        email = user_data['email']
        name = user_data['name']

        # Check if user already exists in DB
        is_admin = False
        user = db.GetUser(username)
        if (user == None):
            # User doesn't exist in DB. Creating new user...
            db.NewUser(username=username, email=email, name=name)
        else:
            log2term('I', f'User {username} is already registered in the database')
            
            # Checking if user, that already exists, is an admin
            admin = db.GetAdmin(username)
            if (admin != None):
                is_admin = True
                log2term('I', f'User {username} is an admin')
            else:
                log2term('I', f'User {username} is not an admin')

        return render_template("dashboard.html",
                               username=username,
                               is_admin=is_admin)


@app.route('/logout')
def LogOut():
    session.clear()
    return redirect(url_for("Index"))


######################## MAIN #########################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
