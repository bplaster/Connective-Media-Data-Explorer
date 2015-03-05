# from pylab import *
# import skimage
# from skimage import io, exposure
# import skimage.io._io as io
# from skimage.data import load
# from skimage.util import img_as_ubyte
import urllib
import urllib2
import cStringIO

# from PIL import Image
from instagram import client, subscriptions
import tweepy
import secret as secret
# from beaker.middleware import SessionMiddleware
from flask import Flask, send_file, redirect, request, session

URL = 'http://104.236.202.250/'
#URL = 'http://localhost:5000/'

session_opts = {
    'session.type': 'ext:memcached',
    'session.data_dir': './session/',
    'session.auto': True,
}

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

auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
auth_twitter.secure = True

# Config Server
app = Flask(__name__) 
app.secret_key = secret.APP_SECRET_KEY 

# @app.before_request
# def setup_request():
#     session = request.environ['beaker.session']

# def process_tag_update(update):
#     print(update)

# reactor = subscriptions.SubscriptionsReactor()
# reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

@app.route('/')
def home():
    try:
        url_instagram = auth_instagram.get_authorize_url(scope=["basic"])
        menu = '<li><a href="%s">Login with Instagram</a></li>' % url_instagram 
        return menu
    except Exception as e:
        print(e)

def get_nav(): 
    nav_menu = ("<h1>Python Instagram</h1>"
                "<ul>"
                    "<li><a href='/process_images'>Process Images</a></li>"
                "</ul>")
            
    return nav_menu

def get_twitter(): 
    menu = "<a href='/twitter_login'>Login with Twitter</a>"
    return menu

@app.route('/twitter_login')
def twitter_auth():
    url = ''
    try:
        url = auth_twitter.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    return redirect(url)


@app.route('/oauth_twitter_callback')
def on_twitter_callback(): 
    code = request.args.get("oauth_verifier")
    auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
    # token = session['request_token']
    # del session['request_token']
    # auth.set_request_token(token[0], token[1])
    session['request_token']= (auth_twitter.request_token.key, auth_twitter.request_token.secret)
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
    #return get_nav()
    return get_twitter()

@app.route('/process_images')
def on_recent(): 
    word = 'cat'
    content = "<h2>User Recent Media</h2>"
    access_token = session.get('access_token_instagram')
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.user_recent_media()
        photo = None
        for media in recent_media:
            # photos.append('<div style="float:left;">')
            if(media.type == 'image'):
                if word in media.caption.text:
                    photo = media.get_low_resolution_url()
                    # Process images
                    # img = Image.open(cStringIO.StringIO(urllib.urlopen(photo).read()))
                    # i = img_as_ubyte(img)  # To convert to uint8 data type
                    break
        if photo == None:
            media, next = api.tag_recent_media(tag_name=word, count=1)
            print(media)
            photo = media[0].get_low_resolution_url()

        display_photo_html = []
        display_photo_html.append('<div style="float:left;">')
        display_photo_html.append('<img src="%s"/>' % (photo))
        print(media)

        content += ''.join(display_photo_html)
    except Exception as e:
        print(e)              
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content, api.x_ratelimit_remaining,api.x_ratelimit)


if __name__ == '__main__':
    # app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.run(debug=True, host='localhost', port=5000)
