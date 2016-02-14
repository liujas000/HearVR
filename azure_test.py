#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import urllib2
# If you are using Python 3+, import urllib instead of urllib2

import json 
import csv
import re

def convertCsv():
    with open('comments/sound_comments.csv', 'rb') as f:
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

        # If you are using Python 3+, replace urllib2 with urllib.request in the above code:
        # req = urllib.request.Request(url, body, headers) 
        # response = urllib.request.urlopen(req)

        result = response.read()
        # result = re.sub('Ää+', '[', result)
        # result = re.sub( 'Åå+'   ,']' , result)
        print type(result)
        d = json.loads(result)
        final_arr = d['Results']['output1']['value']['Values']


    except urllib2.HTTPError, error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))



        