from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from datetime import datetime
from datetime import date
from PyDictionary import PyDictionary
import string
import pandas as pd
project_name = "Best Food Finder"
net_id = "April Ye yy459, Alan Huang ah2294, Geena Lee jl3257, Samuel Chen sc2992, Jack Ding jad493"
features = ['name','description', 'neighbourhood_cleansed', 'bathrooms','bedrooms','price','maximum_nights', 'amenities', 'picture_url', 'listing_url', 'scores','comments','amenities_match']
from nltk.stem import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
import pickle

# import sentiment analysis and stemming
#sia = SentimentIntensityAnalyzer()
ps = PorterStemmer()

loaded_model = pickle.load(open('app/irsystem/controllers/knnpickle_file', 'rb'))
result = loaded_model.predict([[1,1,2000,1125]])
#print(sia.polarity_scores('i like this place'))

def similarity_result(data, keyword):
	'''
	@data : dataframe with  pruned data
	@keyword : list of token in keyword
	'''
	keywordsWithSynonyms = []
	dictionary=PyDictionary(keyword)
	for i, w in enumerate(keyword):
		synonyms = dictionary.getSynonyms()[i]
		keywordsWithSynonyms.append(w)
		if not synonyms is None:
			keywordsWithSynonyms += synonyms[w]
	keywordsWithSynonyms = [ps.stem(w) for w in keywordsWithSynonyms]
	reviews = getreview()
	rank = []
	for i, text in enumerate(data['description']):
		#perform jaccard
		scores = 0
		# remove punctuation
		tokens = text.strip(string.punctuation)
		tokens = tokens.lower().split()
		# stem the token
		tokens = [ps.stem(w) for w in tokens]

		intersection = len(list(set(tokens).intersection(set(keywordsWithSynonyms))))
		union = (len(tokens) + len(keywordsWithSynonyms)) - intersection
		if (union == 0):
			print("union is 0")
		scores += float(intersection) / union

		list_id = data.iloc[i]['id']

		#jaccard on amenities
		amenities = data.iloc[i]['amenities']
		amenities= [ps.stem(w.lower()) for w in amenities]
		intersection = len(list(set(amenities).intersection(set(keywordsWithSynonyms))))
		union = (len(amenities) + len(keywordsWithSynonyms)) - intersection
		scores += float(intersection) / union

		# compute the similairty score for review also
		for rev in reviews[reviews.listing_id == list_id]['comments']:
			tokens = rev.strip(string.punctuation)
			tokens = tokens.lower().split()
			tokens = [ps.stem(w) for w in tokens]
			intersection = len(list(set(tokens).intersection(set(keywordsWithSynonyms))))
			union = (len(tokens) + len(keywordsWithSynonyms)) - intersection
			scores += float(intersection) / union

		rank.append((scores, i))
	rank = sorted(rank, key=lambda tup: tup[0], reverse=True)
	# get the sorted index
	ranked_i = [doc[1] for doc in rank]
	scores = [doc[0] for doc in rank]
	return data.iloc[ranked_i], scores

def getReviews(data):
	total_review = []
	for i in range(len(data)):
		reviews = getreview()
		list_comment = []
		id = data.iloc[i]['id']
		for rev in reviews[reviews.listing_id == id]['comments']:
			list_comment.append(rev)

		total_review.append(list_comment)
	data['comments'] = total_review
	return data

def getAmen(data, query):
	lists = []
	for i in range(len(data)):
		list_amen = []
		for amen in data.iloc[i]['amenities']:
			if(amen.lower() in query):
				list_amen.append(amen)
		lists.append(list_amen)

	data['amenities_match'] = lists
	return data


@irsystem.route('/search', methods=['GET'])
def search():
	print("in search")
	df = getdata()

	#Todo: so far i am not sure how the query will be passed in and how many will be passed so i just put some dummy value

	query = request.args.get('keywords')

	if not query:
		data = []
		output_message = 'No result'
		return render_template('no_results.html')

		#return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
	print(query)
	output_message = "Your search: " + query

	price = int(request.args.get('budget'))
	nbh = request.args.get('neighborhood')
	bedrooms = int(request.args.get('bed'))
	bathrooms = int(request.args.get('bath'))
	start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
	end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
	today_date = datetime.strptime(date.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
	time = (end_date - start_date).days
	start_date_check = (start_date - today_date).days
	print(start_date)
	print('------')
	print(today_date)
	if (time < 0 or start_date_check < 0):
		output_message = "The date you inputted was invalid,"
		if start_date_check < 0:
			output_message += " start date must be after today's date."
		elif time < 0:
			output_message += " end date must be after start date."
		return render_template('no_results.html', output_message=output_message)

	# print(bedrooms)
	# print(bathrooms)
	# print(time)
	price /= time
	knn = False
	if not nbh:
		nbh = loaded_model.predict([[bathrooms,bedrooms,price,time]])[0]
		output_message = ''
		knn = True
	pruned_data = df[(df.neighbourhood_cleansed == nbh) & (df.price <= price) & (df.bedrooms >= bedrooms) & (df.bathrooms >= bathrooms) & (df.maximum_nights >= time)]
	if (len(pruned_data) == 0):
		pruned_data = df[(df.neighbourhood_cleansed == nbh) & (df.bedrooms >= bedrooms) & (df.bathrooms >= bathrooms) & (df.maximum_nights >= time)]
		output_message = 'No results for your query, but you might like these!'
		if (len(pruned_data) == 0):
			pruned_data = df[(df.neighbourhood_cleansed == nbh)]
			output_message = 'No results for your query, but you might like these!'

	res_list, scores= similarity_result(pruned_data, keyword=query.lower().split(','))
	res_list = res_list[:5]
	scores = scores[:5]
	res_list['scores'] = scores
	if len(scores) > 0:
		res_list['scores'] = res_list['scores'].round(3)

	#print(res_list)
	res_list = getReviews(res_list)
	#print(res_list)
	print(res_list['comments'])

	print(res_list['scores'])
	# if jaccard is 0
	if(len(res_list) != 0 and scores[0] == 0):
		res_list = res_list.sort_values('price')
	res_list = getAmen(res_list, query.lower().split(','))
	res_list = res_list[features]

	#res_list['maximum_nights'] = pd.to_numeric(res_list['maximum_nights'], errors='coerce')
	#res_list['bedrooms'] = pd.to_numeric(res_list['bedrooms'], errors='coerce')
	#res_list['bedrooms'].astype(int)
	#res_list['bathrooms'] = pd.to_numeric(res_list['bathrooms'], errors='coerce')
	#res_list['price'] = pd.to_numeric(res_list['price'], errors='coerce')

	#print(res_list)


    # description
    # neighbourhood_cleansed
    # bathrooms
    # bedrooms
    # price
    # maximum_nights
	if(len(res_list) == 0):
		output_message = 'No results for your query'
	if(knn == True):
		output_message += ' Recommended neighborhood: ' + nbh

	return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=res_list.values.tolist())

@irsystem.route('/', methods=['GET'])
def home():
	print("in home")
	return render_template('search.html', name=project_name, netid=net_id)
