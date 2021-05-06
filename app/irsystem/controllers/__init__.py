# Import flask deps
from flask import request, render_template, \
	flash, g, session, redirect, url_for, jsonify, abort

# For decorators around routes
from functools import wraps

# Import for pass / encryption
from werkzeug import check_password_hash, generate_password_hash

# Import the db object from main app module
from app import db

# Marshmallow
from marshmallow import ValidationError

# Import socketio for socket creation in this module
from app import socketio

# Import module models
# from app.irsystem import search

# IMPORT THE BLUEPRINT APP OBJECT
from app.irsystem import irsystem

# Import module models
from app.accounts.models.user import *
from app.accounts.models.session import *
import pandas as pd
import numpy as np
import re
import ast

print('loading data...')
features = ['id','name', 'description', 'neighbourhood_cleansed', 'bathrooms','bedrooms','price','maximum_nights', 'amenities', 'picture_url', 'listing_url']
data = pd.read_csv("app/irsystem/controllers/cleaned_list.csv", encoding = "ISO-8859-1")
data['bathrooms_text'] = data['bathrooms_text'].replace('Half-bath', '0.5 baths')
data['bathrooms_text'] = data['bathrooms_text'].replace('Private half-bath', '0.5 baths')
data['bathrooms_text'] = data['bathrooms_text'].replace('Shared half-bath', '0.5 baths')

data['bathrooms_text'] = data['bathrooms_text'].replace(np.nan, '0', regex=True)
data['bathrooms'] = data.bathrooms_text.str.split().str.get(0).astype(float)
data['bedrooms'] = data['bedrooms'].replace(np.nan, '0', regex=True)
data['bedrooms'] = data.bedrooms.astype(int)

data['price'] = data['price'].replace('[\$,]', '', regex=True).astype(float).round(2)
data['description'] = data['description'].replace(np.nan, '', regex=True)

data['description'] = data['description'].replace(np.nan, '', regex=True)
data['description'] = data['description'].apply(lambda x: re.sub(r'[^\x00-\x7F]+','', x))

data['name'] = data['name'].replace(np.nan, '', regex=True)
data['name'] = data['name'].apply(lambda x: re.sub(r'[^\x00-\x7F]+','', x))
data['amenities'] = data['amenities'].apply(ast.literal_eval)

print('data loaded')

print('load reviews...')

review = pd.read_csv("app/irsystem/controllers/pruned_review.csv")
print('review  loaded')
def getdata():
  return data[features]

def getreview():
    return review
