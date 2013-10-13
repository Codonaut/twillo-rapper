import os
from twilio.rest import TwilioRestClient
from twilio import twiml

from urlparse import urlparse
from pymongo import MongoClient
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)

TWILIO_SID = 'AC5bae5919ad738a13c8c66f63540df289'
TWILIO_AUTH_TOKEN = '100afcb038cb6359d6a2175abbaaaf04'
TWILIO_NUM = '+18563167002'
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
twilio_client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)


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
