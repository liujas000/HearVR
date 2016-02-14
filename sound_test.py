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

def clearFolder():
	folder = '/Users/jasonliu/treehacks/music'
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e
	folder = '/Users/jasonliu/treehacks/comments'
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e


def getId(link):
	client = soundcloud.Client(client_id='7971372eb07dc40788ca558ab6fc8860')
	track = client.get('/resolve', url=link)
	return track.id

def getTrack(track_id):
	r = requests.get("https://api.soundcloud.com/tracks/" + str(track_id) + "/stream?client_id=3aa89c75a3a5e2dd5c46e651ef3191ed")
	mp3_url = r.url
	urllib.urlretrieve(mp3_url, "music/" + str(track_id) +  ".mp3")
	sound = AudioSegment.from_mp3("/Users/jasonliu/treehacks/music/" + str(track_id) + ".mp3")
	sound.export("/Users/jasonliu/treehacks/music/" + str(track_id) + ".wav", format="wav")


def getComments(track_id):
	
	response = urllib2.urlopen('http://api.soundcloud.com/tracks/' + str(track_id) +  '/comments?client_id=7971372eb07dc40788ca558ab6fc8860')
	comment_str = response.read()
	comment_json = json.loads(comment_str)
	comment_json.sort(key=lambda x: x['timestamp'])
	
	employ_data = open('comments/' + str(track_id) +'_old.csv', 'wb')


	csvwriter = csv.writer(employ_data)
	body_json = [(str(x['body'].encode('ascii', 'ignore')), str(x['timestamp']), str(x['user']['username'].encode('ascii', 'ignore'))) for x in comment_json]
	csvwriter.writerow(  ('sentiment_label', 'tweet_text', 'timestamp', 'username') )
	for x in body_json:
		new_body = re.sub('[^A-Za-z]+', ' ', x[0]).lower()
		csvwriter.writerow((0, new_body, x[1], x[2]))



def convertCsv(track_id):
    with open('comments/' + str(track_id) +'_old.csv', 'rb') as f:
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

    url = 'https://ussouthcentral.services.azureml.net/workspaces/862addce0be44e0e8b9dd7ad79b58ef8/services/af0bb6e9205543c3a35a486d114d4338/execute?api-version=2.0&details=true'
    api_key = 'lio1RglkJgFy1ZO0WdEtHlX9MDbJ7KlDIo2+EoWsmX5jesDPek0bajf+Sc/v7woLrpG71tZr/iJWLCFLN+rn0Q==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib2.Request(url, body, headers) 

    try:
        response = urllib2.urlopen(req)

        result = response.read()
        d = json.loads(result)
        final_arr = d['Results']['output1']['value']['Values']
        #employ_data = open('comments/sound_comments_new.csv', 'wb')
        employ_data = open('comments/' + str(track_id) + '.csv', 'wb')
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
	clearFolder()
	arr = open('links.txt').readlines()
	p = Pool(5)
	p.map(f, arr)


## multithreading fail
# class myThread(threading.Thread):

# 	def __init__(self, track_id):
# 		threading.Thread.__init__(self)
# 		self.track_id = track_id
# 	def run(self):
# 		#print 'Processing', link
# 		#track_id = getId(link)
# 		print 'track_id is:', track_id
# 		print 3
# 		getTrack(track_id)
# 		print 4
# 		getComments(track_id)
# 		print 5
# 		convertCsv(track_id)


# if __name__ == "__main__":
# 	print 1
# 	clearFolder()
# 	arr = open('links.txt').readlines()
# 	thread_arr = []
# 	id_arr = []
# 	for link in arr:
# 		id_arr.append(getId(link))
# 	for track_id in id_arr:
# 		thread = myThread(track_id)
# 		thread.start()
# 		thread_arr.append(thread)

# 	for t in thread_arr:
# 		t.join()

# 	print 'done!'



# THIS IS THE WORKING, SEQUENTIAL VERSION
# if __name__ == "__main__":
# 	print 1
# 	clearFolder()
# 	arr = open('links.txt').readlines()
# 	for link in arr:
# 		print 'Processing', link
# 		track_id = getId('https://soundcloud.com/kanyewest/nomorepartiesinlamix1-clean')
# 		print 3
# 		getTrack(track_id)
# 		print 4
# 		getComments(track_id)
# 		print 5
# 		convertCsv(track_id)


