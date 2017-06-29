'''
Understanding the Twitter API v1.1
'''
from twython import Twython

API_KEY = 'INSERT HERE'
API_SECRET = 'INSERT HERE'

ACCESS_TOKEN = 'INSERT HERE'
ACCESS_TOKEN_SECRET = 'INSERT HERE'


twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

#testing our new twitter interface
print twitter.get_user_timeline()

print twitter.get_last_function_header('x-rate-limit-remaining')


#from the How it Works section:
def  twitter_oauth_login():
  API_KEY = 'INSERT HERE'
  API_SECRET = 'INSERT HERE'

  ACCESS_TOKEN = 'INSERT HERE'
  ACCESS_TOKEN_SECRET = 'INSERT HERE'

  twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  return(twitter)


'''
Determining your Twitter followers and friends
'''

twitter = twitter_oauth_login()

friends_ids = twitter.get_friends_ids(count=5000)
friends_ids = friends_ids['ids']

followers_ids = twitter.get_followers_ids(count=5000)
followers_ids = followers_ids['ids']

print len(friends_ids), len(followers_ids)


friends_set = set(friends_ids)
followers_set = set(followers_ids)

print('Number of Twitter users who either are our friend or follow you (union):')
print(len(friends_set.union(followers_set)))

len(friends_set | followers_set)
len(set(friends_ids+followers_ids))

print('Number of Twitter users who follow you and are your friend (intersection):')
print(len(friends_set & followers_set))

print("Number of Twitter users you follow that don't follow you (set difference):")
print(len(friends_set - followers_set))

print("Number of Twitter users who follow you that you don't follow (set difference):")
print(len(followers_set - friends_set))


'''
Pulling Twitter User Profiles
'''


def pull_users_profiles(ids):
    users = []
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        users += twitter.lookup_user(user_id=batch)
        print(twitter.get_lastfunction_header('x-rate-limit-remaining'))
    return (users)

friends_profiles = pull_users_profiles(friends_ids)
followers_profiles = pull_users_profiles(followers_ids)

friends_screen_names = [p['screen_name'] for p in friends_profiles]

print friends_screen_names

#from There's more section

friends_screen_names = [p['screen_name'] for p in friends_profiles if 'screen_name' in p]

friends_screen_names = [p.get('screen_name',{}) for p in friends_profiles]




'''
Making requests without running afoul of Twitter's rate limit
'''

import time
import math

rate_limit_window = 15 * 60 #900 seconds

def pull_users_profiles_limit_aware(ids):
    users = []
    start_time = time.time()
    # Must look up users in
    for i in range(0, len(ids), 10):
        batch = ids[i:i + 10]
        users += twitter.lookup_user(user_id=batch)
        calls_left = float(twitter.get_lastfunction_header('x-rate-limit-remaining'))
        time_remaining_in_window = rate_limit_window - (time.time()-start_time)
        sleep_duration = math.ceil(time_remaining_in_window/calls_left)
        print('Sleeping for: ' + str(sleep_duration) + ' seconds; ' + str(calls_left) + ' API calls remaining')
        time.sleep(sleep_duration)

    return (users)

friends_profiles = pull_users_profiles_limit_aware(friends_ids)
followers_profiles = pull_users_profiles_limit_aware(followers_ids)




'''
Storing JSON data to disk
'''

import json
def save_json(filename, data):
    with open(filename, 'wb') as outfile:
        json.dump(data, outfile)

def load_json(filename):
    with open(filename) as infile:
        data = json.load(infile)
    return data

fname  = 'test_friends_profiles.json'
save_json(fname, friends_profiles)

test_reload = load_json(fname)
print(test_reload[0])

'''
Storing user profiles in MongoDB using PyMongo
'''

import pymongo

host_string = "mongodb://localhost"
port = 27017
mongo_client = pymongo.MongoClient(host_string, port)

# get a reference to the mongodb database 'test'
mongo_db = mongo_client['test']

# get a reference to the 'user profiles' collection in the 'test' database
user_profiles_collection = mongo_db['user_profiles']

user_profiles_collection.insert(friends_profiles)
user_profiles_collection.insert(followers_profiles)


#from How it works section
def save_json_data_to_mongo(data, mongo_db,
                            mongo_db_collection,
                            host_string = "localhost",
                            port = 27017):
    mongo_client = pymongo.MongoClient(host_string, port)
    mongo_db = mongo_client[mongo_db]
    collection = mongo_db[mongo_db_collection]
    inserted_object_ids = collection.insert(data)
    return(inserted_object_ids)


'''
Exploring geographic information available in profiles
'''


fname = 'test_friends_profiles.json'
load_json(fname)


geo_enabled = [p['geo_enabled'] for p in friends_profiles]
print geo_enabled.count(1)


location = [p['location'] for p in friends_profiles]
print location.count('')


print(set(location))

time_zone = [p['time_zone'] for p in friends_profiles]
print time_zone.count(None)
print(set(time_zone))

status_geo = [p['status']['geo'] for p in friends_profiles if ('status' in p and p['status']['geo'] is not None)]
if status_geo: print status_geo[0]
print len(status_geo)



'''
Plotting geo spatial data in Python
'''

status_geo = []
status_geo_screen_names = []
for fp in friends_profiles:
    if ('status' in fp and fp['status']['geo'] is not None and 'screen_name' in fp):
        status_geo.append(fp['status']['geo'])
        status_geo_screen_names.append(fp['screen_name'])



import folium
from itertools import izip

#Let Folium determine the scale
map = folium.Map(location=[48, -102], zoom_start=3)

for sg, sn in izip(status_geo, status_geo_screen_names):
    map.simple_marker(sg['coordinates'], popup=str(sn))

map.create_map(path='us_states.html')
