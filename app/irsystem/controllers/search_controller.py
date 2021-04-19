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

	pruned_data = df[(df.neighbourhood_cleansed == nbh) & (df.price <= price) & (df.bedrooms <= bedrooms) & (df.bathrooms <= bathrooms) & (df.maximum_nights >= time)]

	#Todo peform similairty result
	res_list = similarity_result(pruned_data, keyword=query.split(','))[:5]

	print(res_list)


	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
		print(res_list.values.tolist())

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
