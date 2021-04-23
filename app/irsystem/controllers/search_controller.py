from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import string
project_name = "Best Food Finder"
net_id = "April Ye yy459, Alan Huang ah2294, Geena Lee jl3257, Samuel Chen sc2992, Jack Ding jad493"
features = ['name','description', 'neighbourhood_cleansed', 'bathrooms','bedrooms','price','maximum_nights']
from nltk.stem import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer

# import sentiment analysis and stemming
#sia = SentimentIntensityAnalyzer()
ps = PorterStemmer()

#print(sia.polarity_scores('i like this place'))

def similarity_result(data, keyword):
	'''
	@data : dataframe with  pruned data
	@keyword : list of token in keyword
	'''
	keyword = [ps.stem(w) for w in keyword]
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
		intersection = len(list(set(tokens).intersection(set(keyword))))
		union = (len(tokens) + len(keyword)) - intersection
		scores += float(intersection) / union

		list_id = data.iloc[i]['id']
		# compute the similairty score for review also
		for rev in reviews[reviews.listing_id == list_id]['comments']:
			tokens = rev.strip(string.punctuation)
			tokens = tokens.lower().split()
			tokens = [ps.stem(w) for w in tokens]
			intersection = len(list(set(tokens).intersection(set(keyword))))
			union = (len(tokens) + len(keyword)) - intersection
			scores += float(intersection) / union

		rank.append((scores, i))
	rank = sorted(rank, key=lambda tup: tup[0], reverse=True)
	# get the sorted index
	ranked_i = [doc[1] for doc in rank]
	return data.iloc[ranked_i]

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

@irsystem.route('/search', methods=['GET'])
def search():
	print("in search")
	df = getdata()

	#Todo: so far i am not sure how the query will be passed in and how many will be passed so i just put some dummy value

	query = request.args.get('keywords')

	if not query:
		data = []
		output_message = 'No result'
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
	print(query)

	price = float(request.args.get('budget'))
	nbh = request.args.get('neighborhood')
	bedrooms = float(request.args.get('bed'))
	bathrooms = float(request.args.get('bath'))
	time = float(request.args.get('time')) * 30

	print(bedrooms)
	print(bathrooms)
	print(time)

	pruned_data = df[(df.neighbourhood_cleansed == nbh) & (df.price <= price) & (df.bedrooms >= bedrooms) & (df.bathrooms >= bathrooms) & (df.maximum_nights >= time)]

	#Todo peform similairty result
	res_list = similarity_result(pruned_data, keyword=query.lower().split(','))[:5]
	res_list = getReviews(res_list)
	print(res_list['comments'])

	res_list = res_list[features]
	#print(res_list)


	output_message = "Your search: " + query

    # description
    # neighbourhood_cleansed
    # bathrooms
    # bedrooms
    # price
    # maximum_nights

	return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=res_list.values.tolist())

@irsystem.route('/', methods=['GET'])
def home():
	print("in home")
	return render_template('search.html', name=project_name, netid=net_id)
