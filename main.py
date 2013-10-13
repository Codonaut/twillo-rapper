import os
import logging
from settings import *
from beatcreation import create_beat, get_preset_url, get_hit_url
from twilio.rest import TwilioRestClient
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from twilio import twiml

from urlparse import urlparse
from pymongo import MongoClient
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)

#CREATED BY S&M

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

def get_response_and_digit(request):
	r = twiml.Response()
	digit = request.form.get('Digits', '')
	return r, digit

@app.route('/')
def index():
	bucket = boto_conn.get_bucket('twilio-rapper')
	key = Key(bucket)
	key.key = 'test'
	key.get_contents_from_filename('')
	r = twiml.Response()
	r.say("Welcome to Twilio Beats")
	return str(r)

def generate_intro_twiml(r):
	with r.gather(numDigits=1, action=url_for('.intro_redirect')) as g:
		g.say('To hear presets press 1.  To make your own beats press 2.')
	return r.toxml()

@app.route('/intro_redirect', methods=['POST'])
def intro_redirect():
	r, digit = get_response_and_digit(request)
	if digit == '1':
		return generate_presets_menu_twiml(r)
	elif digit == '2':
		return generate_beat_preview_twiml(r)
	else:
		r.say("You pressed the wrong button bitch.")
		return generate_intro_twiml(r)

@app.route('/twilio_endpoint', methods=['GET'])
def twilio_response():
	r = twiml.Response()
	r.say("Welcome to Rap Twilio")
	return generate_intro_twiml(r)

def generate_presets_menu_twiml(r):
	''' Presets menu for playing presets '''
	with r.gather(numDigits=1, finishOnKey ="",action=url_for('.twilio_preset_handler')) as g:
		g.say('Use the digits 1-9 to preview a beat.  Use 0 to continue and select a beat')

	return r.toxml()

def generate_presets_selection_twiml(r):
	''' Menu to let user select a beat, or go back to main menu '''
	with r.gather(numDigits=1, finishOnKey ="", action=url_for('.twilio_preset_selection_handler')) as g:
		g.say('Enter the beat you would like to rap to, or enter star to return to main menu.')
	return r.toxml()

def generate_presets_twiml(r, sample_url):
	''' Adds a play to the twiml '''
	r.play(sample_url, loop=2)
	return generate_presets_menu_twiml(r)

@app.route('/preset_handler', methods=['POST'])
def twilio_preset_handler():
	''' Preview handler '''
	r, digit = get_response_and_digit(request)
	if digit == '0':
		return generate_presets_selection_twiml(r)
	elif digit == '*':
		return generate_intro_twiml(r)
	elif digit == '#':
		r.say('Invalid input, try again.')
		return generate_presets_menu_twiml(r)
	else:
		url = get_preset_url(digit)
		return generate_presets_twiml(r, url)

@app.route('/preset_selection_handler', methods=['POST'])
def twilio_preset_selection_handler():
	''' Receives a beat selection for the person to rap to '''
	r, digit = get_response_and_digit(request)
	if digit == '*':
		return generate_intro_twiml(r)
	elif digit == '0' or digit == '#':
		r.say('Invalid input.  Try again.')
		return generate_presets_selection_twiml(r)
	else:
		return generate_rap_create(r, get_preset_url(digit) )

def generate_beat_preview_twiml(r):
	with r.gather(numDigits=1, finishOnKey='', action=url_for('.twilio_beat_preview_handler')) as g:
		g.say("Press the 1-8 to try out the different beat sounds. Press 0 when you're done. Press 1 for hihat. 2 for snare. 3 for bass. 4 for hihat and snare. 5 for hihat and bass. 6 for bass and snare. 7 for hihat, bass, and snare. 8 for rest. Press star to go back to the main menu")
	return r.toxml()

@app.route('/twilio_beat_preview_handler', methods=['POST'])
def twilio_beat_preview_handler():
	r, digit = get_response_and_digit(request)
	if digit == '*':
		return generate_intro_twiml(r)
	elif digit == '9' or digit == '#':
		r.say("Invalid Input. Please try again")
		return generate_beat_preview_twiml(r)
	elif digit == '0':
		return generate_beat_creation_twiml(r)
	else: 
		url = get_hit_url(digit)
		return generate_hit_preview(r, url)


def generate_hit_preview(r,url):
	r.pause(length=1)
	r.play(url)
	return generate_beat_preview_twiml(r)

def generate_beat_creation_twiml(r):
	with r.gather(numDigits=8, finishOnKey='*', action=url_for('.twilio_beat_creation_handler')) as g:
		g.say("Input 8 digits to make the beat. Press 1 for hihat. 2 for snare. 3 for bass. 4 for hihat and snare. 5 for hihat and bass. 6 for bass and snare. 7 for hihat, bass, and snare. 8 for rest. Press star to go back to the main menu")
	return r.toxml()

@app.route('/beat_creation_handler', methods=['POST'])
def twilio_beat_creation_handler():
	# Handles beat creation interface
	r, digits = get_response_and_digit(request)

	if digits == '':
		return generate_intro_twiml(r)
	elif not valid(digits):
		r.say('Invalid input.  Try again.')
		return generate_beat_creation_twiml(r)
	else:
		return generate_beat_approval_twiml(r,digits)

def valid(phone_input):
	valid_set = set(['1','2','3','4','5','6','7','8'])
	for c in phone_input:
		if c not in valid_set:
			return False
	return True

def generate_beat_approval_twiml(r, digits):
	r.play(create_beat(digits), loop=4)
	print digits
	with r.gather(numDigits=1, finishOnKey='', action=url_for('.twilio_beat_approval_handler', digits = digits)) as g:
		g.say(" To hear the beat again press 1. To make a new beat press 2. To continue to rapping press 0. To return to the main menu press star")
	return r.toxml()

@app.route('/beat_approval_handler/<digits>', methods=['POST'])
def twilio_beat_approval_handler(digits):
	r, digit = get_response_and_digit(request)
	if digit == "1":
		return generate_beat_approval_twiml(r, digits)
	elif digit == "2":
		return generate_beat_creation_twiml(r)
	elif digit == "*":
		return generate_intro_twiml(r)
	elif digit == "0":
		return generate_rap_create(r, digits)
	else:
		r.say("Invalid input. Please try again")
		return generate_beat_approval_twiml(r, digits)
	      
#dial conference and then record
def generate_rap_create(r, digits):
  with r.dial(record=True,hangupOnStar=True,action=url_for('.twilio_post_rap_processing')) as c:
    c.conference("RapSession")
  twilio_client.calls.create(to="18567848717",from_="18563167002",url=url_for('.twilio_join_rap'),send_digits=digits + "#")
  return r.toxml()
@app.route('/post_rap_processing', methods=['POST'])
def twilio_post_rap_processing():
  pass


@app.route('/beat_call/', methods=['POST'])
def twilio_beat_call():
  r = twiml.Response()
  r.gather(action=url_For('.twilio_play_beat'))
  return r.toxml()

@app.route('/play_beat/', methods=['POST'])
def twilio_play_beat():
  r, digits = get_response_and_digit(request)
  r.play(get_preset_url(digits),loop=0)
  return r.toxml()       

@app.route('/join_rap/', methods=['GET'])
def twilio_join_rap():
  r = twiml.Response()
  with r.dial() as c:
    c.conference("RapSession")

  return r.toxml()

#dial conference and play beat

#after conference play file for other person

@app.route('/beat_playback/<digits>', methods=['GET'])

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
