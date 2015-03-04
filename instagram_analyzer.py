from pylab import *
import skimage
from skimage import io
import skimage.io._io as io
from skimage.data import load
from PIL import Image
from instagram.client import InstagramAPI
from skimage import exposure
from skimage.util import img_as_ubyte
import urllib
import urllib2
import cStringIO
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import secret as client

# API keys
INSTAGRAM_CLIENT_ID = client.INSTAGRAM_CLIENT_ID
INSTAGRAM_CLIENT_SECRET = client.INSTAGRAM_CLIENT_SECRET
INSTAGRAM_ACCESS_TOKEN = client.INSTAGRAM_ACCESS_TOKEN

# # Webdriver
# url = 'https://instagram.com/oauth/authorize/?client_id='
# url += INSTAGRAM_CLIENT_ID
# url += '&redirect_uri=http://tech.cornell.edu/&response_type=token'
# driver = webdriver.Chrome()
# driver.get(url)

api = InstagramAPI(access_token = INSTAGRAM_ACCESS_TOKEN)

#get popular images feed
user_media = api.user_recent_media()[0]

#extract urls of popular images to a list
photolist = []
for media in user_media:
    photolist.append(media.images['standard_resolution'].url)


# process images
for p in photolist:
    im = Image.open(cStringIO.StringIO(urllib.urlopen(p).read()))
    i = img_as_ubyte(im)  # To convert to uint8 data type
    
    #image = exposure.rescale_intensity(i, in_range=(0, 2**7 - 1))
    
    axis('off')
    imshow(i,origin='lower')
    show()