from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Best Food Finder"
net_id = "April Ye yy459, Alan Huang ah2294, Geena Lee jl3257, Samuel Chen sc2992, Jack Ding jad493"

def similarity_result(data, keyword):
	'''
	@data : dataframe with  pruned data
	@keyword : list of token in keyword
	'''
	rank = []
	for i, text in enumerate(data['description']):
		#perform jaccard
		tokens = text.split()
		intersection = len(list(set(tokens).intersection(set(keyword))))
		union = (len(tokens) + len(keyword)) - intersection
		rank.append((float(intersection) / union, i))

	rank = sorted(rank, key=lambda tup: tup[0], reverse=True)
	# get the sorted index
	ranked_i = [doc[1] for doc in rank]
	return data.iloc[ranked_i]


@irsystem.route('/search', methods=['GET'])
def search():
	df = getdata()
	print(df['price'][1])

	#Todo: so far i am not sure how the query will be passed in and how many will be passed so i just put some dummy value

	price = request.args.get('price')
	max_night = request.args.get('maximum_night')
	bedrooms = request.args.get('bedrooms')
	query = request.args.get('keyword')

	pruned_data = df[(df.maximum_nights < max_night) & (df.price <= price) & (df.bedrooms <= bedrooms)]

	#Todo peform similairty result
	res_list = similarity_result(pruned_data, keyword=query.split())


	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

@irsystem.route('/', methods=['GET'])
def home_page():
	return render_template('search.html', name=project_name, netid=net_id)