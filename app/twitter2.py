#!/usr/bin/env python
# encoding: utf-8
 
import tweepy
import csv
import time
import json
import os
import nltk
import re
import itertools
from nltk.corpus import stopwords
 
#Twitter API credentials
consumer_key = 'raTV2bT4CKuRqXaPbmcFHxTJh'#keep the quotes, replace this with your consumer key
consumer_secret = 'H8EUBot4exSD7cL1qQDkwRsHkdqNPu81xSII1MjfVIYRsMILPJ'#keep the quotes, replace this with your consumer secret key
access_key = '469683422-r8dOS3YxW0sRfcbLRoVDX8JOabV7lV1UKJtjAmDr'#keep the quotes, replace this with your access token
access_secret = '52Njqdo6ILKHkZTLNQA5pOOs9EXB08sZxNaak3NzZubLg'#keep the quotes, replace this with your access token secret

 
def get_all_tweets(screen_name, api, attempts=0):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	try:
		print screen_name
		#authorize twitter, initialize tweepy
		# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		# auth.set_access_token(access_key, access_secret)
		# api = tweepy.API(auth)
		
		#initialize a list to hold all the tweepy Tweets
		alltweets = []	
		
		#make initial request for most recent tweets (200 is the maximum allowed count)
		new_tweets = api.user_timeline(screen_name = screen_name,count=20)
		
		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#save the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		#keep grabbing tweets until there are no tweets left to grab
		# while len(new_tweets) > 0:
		# 	print "getting tweets before %s" % (oldest)
			
		# 	#all subsiquent requests use the max_id param to prevent duplicates
		# 	new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
			
		# 	#save most recent tweets
		# 	alltweets.extend(new_tweets)
			
		# 	#update the id of the oldest tweet less one
		# 	oldest = alltweets[-1].id - 1
			
		# 	print "...%s tweets downloaded so far" % (len(alltweets))
		
		#transform the tweepy tweets into a 2D array that will populate the csv	 
		
		return [tweet.text.encode("utf-8") for tweet in alltweets]

	except Exception,e: 
		
		if("limit" in str(e)):
			print "waiting 7 minutes ..."
			for i in range(7):
				print i
				time.sleep(60) #Wait 25 minutes! 
			get_all_tweets(screen_name, api, attempts)
		else:
			print "Not authorized for: " + screen_name
			
		
 

def get_current_users():
	path = "tweets/"
	files = []
	for name in os.listdir(path):
		if os.path.isfile(os.path.join(path, name)):
			files.append(os.path.splitext(name)[0])
	return files


def replacement(match):
    return match.group(1).lower();

#*******************************************
#Cleans a tweet
#******************************************    
def clean_tweet(string):

	STOPWORDS = stopwords.words('english')
	STOPWORDS2 = stopwords.words('spanish')
	ignore_words = ['rt', 'co', 'http', 'l']
	string = re.sub(r"('s)", "", string)
	string = re.sub(r'([A-Z])', replacement, string)
	string = re.sub(r'([-_])', " ", string)
	string = re.sub(r'([^a-zA-Z ])', " ", string)
	string = re.sub(r'([\s]+)', " ", string) 
	string = ' '.join([w for w in string.split() if w not in STOPWORDS and w not in STOPWORDS2 and w not in ignore_words])
	
	if len(string) == 1:
		string = ""
	return string

# def read_words(username):
# 	words_dictionary = {}
# 	flag = True
# 	file_name = username+".csv"

# 	for line in file('tweets/'+file_name):
# 		if flag == False:
# 			line = line.strip().split(',')
# 			if len(line) == 3:
# 				tweet = clean_tweet(line[2])
# 				tweet = tweet.split()
# 				for word in tweet:
# 					if word not in words_dictionary:
# 						words_dictionary[word] = 1
# 					else:
# 						words_dictionary[word] += 1
# 		flag = False

# 	return words_dictionary

def read_words(tweets):
	words_dictionary = {}

	for tweet in tweets:
		tweet = clean_tweet(tweet)
		tweet = tweet.split()
		for word in tweet:
			if word not in words_dictionary:
				words_dictionary[word] = 1
			else:
				words_dictionary[word] += 1
	return words_dictionary

def change_scale(current_val, current_min, current_max, final_min, final_max):
	return (((final_max-final_min)*(current_val-current_min))/(current_max-current_min))+final_min;

def paginate(iterable, page_size):
    while True:
        i1, i2 = itertools.tee(iterable)
        iterable, page = (itertools.islice(i1, page_size, None),
                list(itertools.islice(i2, page_size)))
        if len(page) == 0:
            break
        yield page

# if __name__ == '__main__':
def generate_visualization(api):
	ignore_users = []

	#Set up the API with the required keys and tokens...
	# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	# auth.set_access_token(access_key, access_secret)
	# api = tweepy.API(auth)

	#Get all users for which we already have tweets:
	current_users = [] #get_current_users()
	user_images = {}
	tweets = {}

	print "Current Users: "
	print current_users
	#Get the screen_name of the user using our app
	
	try:
		username = api.me().screen_name.replace("u'", "")
		user_images[username] = api.me().profile_image_url.replace("u'", "")
	except Exception, e:
		print str(e)
		if("limit" in str(e)):
			print "waiting 7 minutes ..."
			for i in range(7):
				print i
				time.sleep(60) #Wait 25 minutes! 
			username = api.me().screen_name
			user_images[username] = api.me().profile_image_url
		
	#Download all tweets from that user and save them in a file called username.csv
	if username not in current_users:
		tweets[username] = get_all_tweets(username, api)
		

	#Iterate through the users followers and get their tweets and profile pics
	followers_users = []
	followers = api.followers_ids(username)
	for page in paginate(followers, 30):
		results = api.lookup_users(user_ids=page)
		for follower in results:
		    follower_user_name = follower.screen_name
		    followers_users.append(follower_user_name)
		    user_images[follower_user_name] = follower.profile_image_url
		    if follower_user_name not in ignore_users:
		    	if follower_user_name not in current_users:
		    		tweets[follower_user_name] = get_all_tweets(follower_user_name, api)


	#Now that we have all the tweets from our user and his followers:
	words_dictionary = {}
	words_dictionary[username] = read_words(tweets[username])
	for follower in followers_users:
		words_dictionary[follower] = read_words(tweets[follower])

	#Now that we have all the words and word count per user:
	connections_list = []

	max_common_words = 0
	max_len = 0
	for user in words_dictionary:
		if user != username:
			#Get the word shared the most and the number of times
			current_word = ""
			current_count = 0
			number_common_words = 0
			for word in words_dictionary[username]:
				if word in words_dictionary[user]:
					number_common_words += 1
					temp_count = min(words_dictionary[user][word], words_dictionary[username][word] )
					if temp_count > current_count:
						current_word = word
						current_count = temp_count

			
			if max_common_words < number_common_words:
				max_common_words = number_common_words

			if max_len < len(current_word):
				max_len = len(current_word)
			
			if current_count > 0:
				connections_list.append((username, user, current_word, current_count , change_scale(number_common_words, 0, max_common_words, 1, 7), change_scale(len(current_word), 0, max_len, 130, 300)))


	print connections_list

	data = {}
	data['nodes'] = []
	data['links'] = []
	data['nodes'].append({'name':username, 'group':0, 'rad': 10, 'type': 'grav', 'image_url': user_images[username]})

	unique_words = {}
	max_unique_words = 0
	max_len = 0
	for element in connections_list:
		if element[2] not in unique_words:
			unique_words[element[2]] = 0
		else:
			unique_words[element[2]] += 1

		if max_unique_words < unique_words[element[2]]:
			max_unique_words = unique_words[element[2]]

		if max_len < len(element[2]):
				max_len = len(element[2])

	counter = 0
	node_counter = 1
	word_group = {}
	word_val = {}
	word_nodes = []

	for word in unique_words:
		counter += 1
		word_group[word] = counter;
		data['nodes'].append({'name':word, 'group':counter, 'rad': change_scale(unique_words[word], 0, max_unique_words, 7, 10), 'type': 'grav', 'image_url':'http://s3-eu-west-1.amazonaws.com/petrus-blog/placeholder.png'})
		data['links'].append({'source': 0, 'target':counter, 'stroke': 2, 'length': 350, 'word':word, 'value': 'visible'})
		node_counter += 1
	
	# for i in range(node_counter):
	# 	for j in range(node_counter):
	# 		if(j < i):
	# 			data['links'].append({'source': i, 'target':j, 'stroke': 2, 'length': 500, 'word':word, 'value': 'invisible'})

	link_list = {}
	for element in connections_list:
		data['nodes'].append({'name':element[1], 'group':word_group[element[2]], 'rad': 3, 'type': 'grav', 'image_url': user_images[element[1]]})
		data['links'].append({'source': node_counter, 'target':word_group[element[2]], 'stroke': 2, 'length': 50, 'word':'', 'value': 'visible' })
		#link_list[word_group[element[2]]] = 
		node_counter += 1




	# 	if word_group[element[2]] not in links_list:
	# 		links_list[word_group[element[2]]] = []
		
	# 	links_list[word_group[element[2]]].append(node_counter)
	# 	node_counter += 1
	
	# for link in links_list:
	# 	for link2 in links_list[link]:
	# 		for link3 in lins_list[link]:
	# 			data['links'].append({'source': link2, 'target':link3, 'stroke': 2, 'length': 150, 'word':'', 'value': ''})
	# # 			#data['links'].append({'source': link2, 'target':0, 'stroke': 2, 'length': 200, 'word':'', 'value': ''})

	with open('json/'+username+'.json', 'wt') as out:
		res = json.dump(data, out, sort_keys=True, indent=4, separators=(',', ': '))



			#connections_list.append(username, user)















