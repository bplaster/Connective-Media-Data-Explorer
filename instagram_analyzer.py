# from pylab import *
# import skimage
# from skimage import io, exposure
# import skimage.io._io as io
# from skimage.data import load
# from skimage.util import img_as_ubyte
import urllib
import urllib2
import cStringIO

from PIL import Image
from instagram import client, subscriptions
import tweepy
import secret as secret
# from beaker.middleware import SessionMiddleware
from flask import Flask, send_file, redirect, request, session


session_opts = {
    'session.type': 'ext:memcached',
    'session.data_dir': './session/',
    'session.auto': True,
}

# API keys
CONFIG_INSTAGRAM = {
    'client_id': secret.INSTAGRAM_CLIENT_ID,
    'client_secret': secret.INSTAGRAM_CLIENT_SECRET,
    'redirect_uri': 'http://localhost:5000/oauth_instagram_callback',
}
CONFIG_TWITTER = {
    'consumer_id': secret.TWITTER_CONSUMER_ID,
    'consumer_secret': secret.TWITTER_CONSUMER_SECRET,
    'redirect_uri': 'http://localhost:5000/oauth_twitter_callback',
    'client_id': secret.TWITTER_CLIENT_ID,
    'client_secret': secret.TWITTER_CLIENT_SECRET
}

auth_instagram = client.InstagramAPI(**CONFIG_INSTAGRAM)

auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
auth_twitter.secure = True

# Config Server
URL = 'http://localhost:5000/'
app = Flask(__name__)  


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
        url = auth_instagram.get_authorize_url(scope=["basic"])
        return '<a href="%s">Login with Instagram</a>' % url
    except Exception as e:
        print(e)

def get_nav(): 
    nav_menu = ("<h1>Python Instagram</h1>"
                "<ul>"
                    "<li><a href='/process_images'>Process Images</a></li>"
                "</ul>")
            
    return nav_menu

def twitter_auth():
    url = ''
    try:
        url = auth_twitter.get_authorization_url()
        session['request_token']= (auth_twitter.request_token.key, auth_twitter.request_token.secret)
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    return redirect(url)


@app.route('/oauth_twitter_callback')
def on_twitter_callback(): 
    code = request.args.get("oauth_verifier")
    auth_twitter = tweepy.auth.OAuthHandler(CONFIG_TWITTER['consumer_id'], CONFIG_TWITTER['consumer_secret'])
    token = session['request_token']
    del session['request_token']
    auth.set_request_token(token[0], token[1])

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
    return twitter_auth()

@app.route('/process_images')
def on_recent(): 
    content = "<h2>User Recent Media</h2>"
    access_token = session.get('access_token_instagram')
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.user_recent_media()
        photos = []
        display_photo_html = []
        for media in recent_media:
            # photos.append('<div style="float:left;">')
            if(media.type == 'image'):
                # photos.append('<img src="%s"/>' % (media.get_low_resolution_url()))
                # photos.append(media.get_low_resolution_url())
                photo = media.get_low_resolution_url()
                # Process images
                img = Image.open(cStringIO.StringIO(urllib.urlopen(photo).read()))
                # i = img_as_ubyte(img)  # To convert to uint8 data type

                # TODO: Check image
                display_photo_html = []
                display_photo_html.append('<div style="float:left;">')
                display_photo_html.append('<img src="%s"/>' % (photo))
                print(media)
        content += ''.join(display_photo_html)
    except Exception as e:
        print(e)              
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content, api.x_ratelimit_remaining,api.x_ratelimit)

# # extract urls to a list
# photolist = []
# for media in user_media:
#     photolist.append(media.images['standard_resolution'].url)


# # process images
# for p in photolist:
#     im = Image.open(cStringIO.StringIO(urllib.urlopen(p).read()))
#     i = img_as_ubyte(im)  # To convert to uint8 data type
    
#     #image = exposure.rescale_intensity(i, in_range=(0, 2**7 - 1))
    
#     axis('off')
#     imshow(i,origin='lower')
#     show()

# @route('/media_like/<id>')
# def media_like(id): 
#     access_token = request.session['access_token']
#     api = client.InstagramAPI(access_token=access_token)
#     api.like_media(media_id=id)
#     redirect("/recent")

# @route('/media_unlike/<id>')
# def media_unlike(id): 
#     access_token = request.session['access_token']
#     api = client.InstagramAPI(access_token=access_token)
#     api.unlike_media(media_id=id)
#     redirect("/recent")

# @route('/user_media_feed')
# def on_user_media_feed(): 
#     access_token = request.session['access_token']
#     content = "<h2>User Media Feed</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         media_feed, next = api.user_media_feed()
#         photos = []
#         for media in media_feed:
#             photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
#         counter = 1
#         while next and counter < 3:
#             media_feed, next = api.user_media_feed(with_next_url=next)
#             for media in media_feed:
#                 photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
#             counter += 1
#         content += ''.join(photos)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/location_recent_media')
# def location_recent_media(): 
#     access_token = request.session['access_token']
#     content = "<h2>Location Recent Media</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         recent_media, next = api.location_recent_media(location_id=514276)
#         photos = []
#         for media in recent_media:
#             photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
#         content += ''.join(photos)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/media_search')
# def media_search(): 
#     access_token = request.session['access_token']
#     content = "<h2>Media Search</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         media_search = api.media_search(lat="37.7808851",lng="-122.3948632",distance=1000)
#         photos = []
#         for media in media_search:
#             photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
#         content += ''.join(photos)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/media_popular')
# def media_popular(): 
#     access_token = request.session['access_token']
#     content = "<h2>Popular Media</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         media_search = api.media_popular()
#         photos = []
#         for media in media_search:
#             photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
#         content += ''.join(photos)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/user_search')
# def user_search(): 
#     access_token = request.session['access_token']
#     content = "<h2>User Search</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         user_search = api.user_search(q="Instagram")
#         users = []
#         for user in user_search:
#             users.append('<li><img src="%s">%s</li>' % (user.profile_picture,user.username))
#         content += ''.join(users)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/user_follows')
# def user_follows(): 
#     access_token = request.session['access_token']
#     content = "<h2>User Follows</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         # 25025320 is http://instagram.com/instagram
#         user_follows, next = api.user_follows('25025320')
#         users = []
#         for user in user_follows:
#             users.append('<li><img src="%s">%s</li>' % (user.profile_picture,user.username))
#         while next:
#             user_follows, next = api.user_follows(with_next_url=next)
#             for user in user_follows:
#                 users.append('<li><img src="%s">%s</li>' % (user.profile_picture,user.username))
#         content += ''.join(users)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/location_search')
# def location_search(): 
#     access_token = request.session['access_token']
#     content = "<h2>Location Search</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         location_search = api.location_search(lat="37.7808851",lng="-122.3948632",distance=1000)
#         locations = []
#         for location in location_search:
#             locations.append('<li>%s  <a href="https://www.google.com/maps/preview/@%s,%s,19z">Map</a>  </li>' % (location.name,location.point.latitude,location.point.longitude))
#         content += ''.join(locations)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/tag_search')
# def tag_search(): 
#     access_token = request.session['access_token']
#     content = "<h2>Tag Search</h2>"
#     if not access_token:
#         return 'Missing Access Token'
#     try:
#         api = client.InstagramAPI(access_token=access_token)
#         tag_search, next_tag = api.tag_search(q="catband")
#         tag_recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name)
#         photos = []
#         for tag_media in tag_recent_media:
#             photos.append('<img src="%s"/>' % tag_media.get_standard_resolution_url())
#         content += ''.join(photos)
#     except Exception as e:
#         print(e)              
#     return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(),content,api.x_ratelimit_remaining,api.x_ratelimit)

# @route('/realtime_callback')
# @post('/realtime_callback')
# def on_realtime_callback():
#     mode = request.GET.get("hub.mode")
#     challenge = request.GET.get("hub.challenge")
#     verify_token = request.GET.get("hub.verify_token")
#     if challenge: 
#         return challenge
#     else:
#         x_hub_signature = request.header.get('X-Hub-Signature')
#         raw_response = request.body.read()
#         try:
#             reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
#         except subscriptions.SubscriptionVerifyError:
#             print("Signature mismatch")
if __name__ == '__main__':
    # app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.secret_key = secret.APP_SECRET_KEY
    app.run(debug=True, host='localhost')
