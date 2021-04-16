from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Best Food Finder"
net_id = "April Ye yy459, Alan Huang ah2294, Geena Lee jl3257, Samuel Chen sc2992, Jack Ding jad493"

@irsystem.route('/', methods=['GET'])
def search():
	df = getdata()
	print(df['price'][1])
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



