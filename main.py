from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)
#from pymongo import MongoClient

DEBUG = True
#conn = MongoClient()
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
	return 'Hello World'

#if __name__ == '__main__':
#	app.run()
