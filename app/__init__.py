import urllib
import urllib2
import cStringIO
import twitter2 as tw
import os

from instagram import client, subscriptions
import tweepy
import secret as secret
from flask import Flask, send_file, redirect, request, render_template, json

#URL = 'http://104.236.202.250/'
URL = 'http://localhost:5000/'
session = dict()

# Config Server
app = Flask(__name__) 
app.secret_key = secret.APP_SECRET_KEY


# API keys
CONFIG_INSTAGRAM = {
    'client_id': secret.INSTAGRAM_CLIENT_ID,
    'client_secret': secret.INSTAGRAM_CLIENT_SECRET,
    'redirect_uri': URL+'oauth_instagram_callback',
}
CONFIG_TWITTER = {
    'consumer_id': secret.TWITTER_CONSUMER_ID,
    'consumer_secret': secret.TWITTER_CONSUMER_SECRET,
    'redirect_uri': URL+'oauth_twitter_callback',
}

auth_instagram = client.InstagramAPI(**CONFIG_INSTAGRAM)
auth_twitter = None

@app.route('/')
def home():
    try:
        url_instagram = auth_instagram.get_authorize_url(scope=["basic"])
        menu = '<li><a href="%s">Login with Instagram</a></li>' % url_instagram 
        return menu
    except Exception as e:
        print(e)

def get_nav(): 
    nav_menu = ("<h1>Connective Media Social Data Explorer</h1>"
                "<ul>"
                    "<li><a href='/process_user'>Begin</a></li>"
                "</ul>")
            
    return nav_menu

def get_twitter(): 
    menu = "<a href='/twitter_login'>Login with Twitter</a>"
    return menu

@app.route('/twitter_login')
def twitter_auth():
    url = ''
    auth_twitter = tweepy.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'], CONFIG_TWITTER['redirect_uri'])
    try:
        url = auth_twitter.get_authorization_url()
        session['request_token'] = auth_twitter.request_token
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    return redirect(url)


@app.route('/oauth_twitter_callback')
def on_twitter_callback(): 
    code = request.args["oauth_verifier"]
    auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
    token = session['request_token']
    del session['request_token']
    auth_twitter.request_token = token
    if not code:
        return 'Missing code'
    try:
        access_token = auth_twitter.get_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = tweepy.API(auth_twitter)
        session['access_token_twitter'] = access_token
        print ("access token twitter =" + access_token)
    except Exception as e:
        print(e)
    return get_nav()

@app.route('/oauth_instagram_callback')
def on_instagram_callback(): 
    code = request.args.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = auth_instagram.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token)
        session['access_token_instagram'] = access_token
        print ("access token instagram=" + access_token)
    except Exception as e:
        print(e)
    return get_twitter()

@app.route('/process_user')
def on_recent():
    username = ''
    try:
        auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
        token_twitter = session['access_token_twitter']
        auth_twitter.set_access_token(token_twitter[0], token_twitter[1])
        api_twitter = tweepy.API(auth_twitter)
        token_instagram = session.get('access_token_instagram')
        api_instagram = client.InstagramAPI(access_token=token_instagram)

        return display_visualization(tw.generate_visualization(api_twitter, api_instagram))
    except Exception as e:
        print(e)

@app.route('/process_user/<data>')
def display_visualization(data):
    # SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(SITE_ROOT, "static/data", username+".json")
    # data = json.load(open(json_url))
    return render_template("base.html", data=data)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
