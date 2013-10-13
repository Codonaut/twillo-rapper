import urlparse
import os
from pymongo import MongoClient
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)

TWILIO_SID = 'AC5bae5919ad738a13c8c66f63540df289'
TWILIO_AUTH_TOKEN = '100afcb038cb6359d6a2175abbaaaf04'

MONGO_URL = os.environ.get('MONGOHQ_URL')
if MONGO_URL:
  # Get a connection
  conn = MongoClient(MONGO_URL)
  # Get the database
  db = conn[urlparse(MONGO_URL).path[1:]]
else:
  # Not on an app with the MongoHQ add-on, do some localhost action
  connection = MongoClient()
  db = connection['RapDB']

DEBUG = True
#conn = MongoClient()
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
	return 'Hello World'

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
