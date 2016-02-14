import urllib2
import json
import soundcloud
import csv
import re
import os, shutil
import requests
import urllib
import threading
from pydub import AudioSegment
from multiprocessing import Pool

global MUSIC_DIR, COMMENT_DIR, SC_CLIENT_ID, AZURE_API_KEY, AZURE_URL
# MUSIC_DIR = '/Users/jasonliu/treehacks/music/'
# COMMENT_DIR = '/Users/jasonliu/treehacks/comments/'


def clearFolder():
	folder = MUSIC_DIR
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e
	folder = COMMENT_DIR
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e


def getId(link):
	global SC_CLIENT_ID
	client = soundcloud.Client(client_id= SC_CLIENT_ID)
	track = client.get('/resolve', url=link)
	return track.id

def getTrack(track_id):
	global SC_CLIENT_ID
	r = requests.get("https://api.soundcloud.com/tracks/" + str(track_id) + "/stream?client_id=" + str(SC_CLIENT_ID))
	mp3_url = r.url
	urllib.urlretrieve(mp3_url, MUSIC_DIR + str(track_id) +  ".mp3")
	sound = AudioSegment.from_mp3(MUSIC_DIR + str(track_id) + ".mp3")
	sound.export(MUSIC_DIR + str(track_id) + ".wav", format="wav")


def getComments(track_id):
	
	response = urllib2.urlopen('http://api.soundcloud.com/tracks/' + str(track_id) +  '/comments?client_id=' + str(SC_CLIENT_ID))
	comment_str = response.read()
	comment_json = json.loads(comment_str)
	comment_json.sort(key=lambda x: x['timestamp'])
	
	employ_data = open(COMMENT_DIR + str(track_id) +'_old.csv', 'wb')


	csvwriter = csv.writer(employ_data)
	body_json = [(str(x['body'].encode('ascii', 'ignore')), str(x['timestamp']), str(x['user']['username'].encode('ascii', 'ignore'))) for x in comment_json]
	csvwriter.writerow(  ('sentiment_label', 'tweet_text', 'timestamp', 'username') )
	for x in body_json:
		new_body = re.sub('[^A-Za-z]+', ' ', x[0]).lower()
		csvwriter.writerow((0, new_body, x[1], x[2]))



def convertCsv(track_id):
	global AZURE_API_KEY, AZURE_URL
	with open(COMMENT_DIR + str(track_id) +'_old.csv', 'rb') as f:
		reader = csv.reader(f)
		your_list = list(reader)

	value_arr =  your_list[1:]
	data =  {
	"Inputs": {

	        "input1":
	        {
	            "ColumnNames": ["sentiment_label", "tweet_text", "timestamp", "username"],
	            "Values": value_arr
	        },        },
	    "GlobalParameters": {}
	}

	body = str.encode(json.dumps(data))

	url = AZURE_URL
	api_key = str(AZURE_API_KEY)
	headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

	req = urllib2.Request(url, body, headers) 

	try:
		response = urllib2.urlopen(req)

		result = response.read()
		d = json.loads(result)
		final_arr = d['Results']['output1']['value']['Values']
		employ_data = open(COMMENT_DIR + str(track_id) + '.csv', 'wb')
		csvwriter = csv.writer(employ_data)
		csvwriter.writerow(  ('label', 'score', 'comment', 'timestamp', 'username') )
		for x in final_arr:
			csvwriter.writerow((x[0], x[1], x[2], x[3], x[4]))

	except urllib2.HTTPError, error:
		print("The request failed with status code: " + str(error.code))
		print(error.info())
		print(json.loads(error.read()))

def f(link):
	print 'Processing', link
	track_id = getId(link)
	print 3
	getTrack(track_id)
	print 4
	getComments(track_id)
	print 5
	convertCsv(track_id)

#multiprocessing attempt WORKED
if __name__ == '__main__':
	global SC_CLIENT_ID, AZURE_API_KEY, AZURE_URL, MUSIC_DIR, COMMENT_DIR
	MUSIC_DIR = os.getcwd() + '/music/'
	COMMENT_DIR = os.getcwd() + '/comments/'
	data = json.loads(open('secret.json').read())
	SC_CLIENT_ID =  data['sc_client_id']
	AZURE_API_KEY = data['azure_api_key']
	AZURE_URL = data['azure_url']

	clearFolder()
	arr = open('links.txt').readlines()
	p = Pool(5)
	p.map(f, arr)
