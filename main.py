import os
from settings import *
from music_scripts import beatcreation
from twilio.rest import TwilioRestClient
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from twilio import twiml

from urlparse import urlparse
from pymongo import MongoClient
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
twilio_client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

MONGO_URL = os.environ.get('MONGOHQ_URL')
if MONGO_URL:
  # Get a connection
  conn = MongoClient(MONGO_URL)
  # Get the database
  db = conn[urlparse(MONGO_URL).path[1:]]
else:
  # Not on an app with the MongoHQ add-on, do some localhost action
  conn = MongoClient()
  db = conn['RapDB']


@app.route('/')
def index():
	bucket = boto_conn.get_bucket('twilio-rapper')
	key = Key(bucket)
	key.key = 'test'
	key.get_contents_from_filename('')
	r = twiml.Response()
	r.say("Welcome to Twilio Beats")
	return str(r)

@app.route('/twilio_endpoint', methods=['GET'])
def twilio_response():
	r = twiml.Response()
	r.say("Welcome to Twilio Beats")
	return str(r)

@app.route('/save_name', methods=['GET'])
def save_name():
	names = db.names
	names.insert({"name": request.args['name']})
	return "saved"

@app.route('/print_names', methods=['GET'])
def print_names():
	names = db.names
	return ', '.join([n['name'] for n in names.find()])

if not MONGO_URL:
	if __name__ == '__main__':
		app.run()
