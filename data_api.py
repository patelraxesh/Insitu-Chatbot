import argparse, os, json, requests

#CONSTANTS
access_token = os.environ.get("DATA_API_ACCESS_TOKEN")

#THE MAIN STUFF
def check_folder(newpath):
	if not os.path.exists(newpath):
		os.makedirs(newpath)

def create_json_file(data, filename):
    with open(filename+'.json', 'w') as json_file:
        json.dump(data,json_file)
    
def read_json_file(filename):
  with open(filename+'.json', 'r') as json_file:
    data = json.load(json_file)
  return data

# API DOC - https://insituhackathon.blob.core.windows.net/web/insitusales_examples.html
product_list = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/product/list/'
customer_list = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/customer/list/'
customer_query = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/customer/'
customer_invoices = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/invoice/list/'
order_status = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/order/status/'
email_auth = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/authenticate/status/'

get_url = {'product_list':product_list,
	'customer_list':customer_list,
	'customer_query':customer_query,
	'customer_invoices':customer_invoices,
	'order_status':order_status,
	'email_auth':email_auth}


"""
param: label of the value to be retrieved such as id, status
val:
url: API url mapping stored in a local variable
optional_param:

Examples:
print get_entry('name','110 Bagel Market Bistro','customer_query','1289928')
print get_entry('id',customer_id,'customer_invoices',str(customer_id))
"""
def get_entry(param,val,url,optional_param = ''):
	if optional_param == '':
		r = requests.get(get_url[url]+access_token)
	else:
		r = requests.get(get_url[url]+optional_param+'/'+access_token)
	output = r.json()
	return_list = []
	for i in output:
		if i[param]==val:
			return_list.append(i)
	return return_list[0] if len(return_list)==1 else return_list


"""
Requirement: API call must return one and only one record
"""
#TODO combine into get_entry with handling since this returns a single entry not a set
def get_entry_order_status(target_param,invoice_id):
	url = "https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/order/status/"
	r = requests.get(url+str(invoice_id)+"/"+access_token)
	output = r.json()
	return output[target_param]

def get_key_value_list(inp, param):
	return_list = []

def create_customer(email):
	url = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/customer/create/'
	data = {"name":"R U",
		"address":"OSCO-DRUG 6351 S. PULASKI RD",
		"address2":"",
		"city":"CHICAGO",
		"state":"IL",
		"zipcode":"00000",
		"contact":"ru",
		"phone":"1213231",
		"email":email,
		"latitude":"34.9121733",
		"longitude":"-77.23188189999999"}
	return requests.post(url+access_token, data = data).json()

def place_order(customer_id):
	url = 'https://tcedk8i2p6.execute-api.us-east-1.amazonaws.com/latest/order/create/'
	data = {"customerId":customer_id,
		"customerAddress":"OSCO-DRUG 6351 S. PULASKI RD",
		"orderTotalValue":"1106",
		"orderItemQuantity":["123"],
		"orderItemId":"168234"}
	return requests.post(url+access_token, data = data).text

def get_product_names():
	output = requests.get(product_list+access_token).json()
	return_list = []
	for i in output:
		return_list.append(i['name'])
	return return_list

def get_product_list():
	r = requests.get(get_url['product_list']+access_token).json()
	return r

def get_customer_list():
	r = requests.get(get_url['customer_list']+access_token).json()
	return r

def get_invoices(customer_id):
	r = requests.get(get_url['customer_invoices']+str(customer_id)+"/"+access_token).json()
	return r

def get_order_status(order_id):
	r = requests.get(get_url['order_status']+str(order_id)+"/"+access_token).json()
	return r

def get_email_authentication(email):
	r = requests.get(get_url['email_auth']+str(email)+"/"+access_token).json()
	return r

def get_all_orders(invoices):
	orders = []
	for invoice in invoices:
		orders.append(invoice["id"])
	return orders

def get_customer_email(customer_id):
	r = requests.get(get_url['customer_query']+str(customer_id)+"/"+access_token).json()
	return r['email']

#print get_product_list()
'''
for i in range(len(names)):
	r = requests.get(product_list+access_token)
	output = r.json()
	create_json_file(output, 'product_list')


def save_file(url, filename):

	r = requests.get(url, stream=True)
	if r.status_code == 200:
		with open('temp/'+filename+'.jpg', 'wb') as f:
			for chunk in r:
				f.write(chunk)

for i in range(101,301):
	url = 'http://totallylookslike.tumblr.com/page/'
	r = requests.get(url+str(i))
	soup = BeautifulSoup(r.text, 'html.parser')
	links = sorted(soup.find_all('a'))

	for link in range(len(links)):
		if links[link].find('img') != None: 
			obj = links[link].find('img')
			url = (obj['src'])
			string = (obj['alt'])
			filename = ''
			for letter in string:
				if letter.isalnum() or letter==' ':
					filename += letter
			if filename == '': filename = str(i)+'_'+str(link)
			save_file(url,filename)
'''