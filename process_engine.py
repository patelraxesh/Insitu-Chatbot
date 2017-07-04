import zipfile, gmplot, os
from data_api import get_entry, get_entry_order_status, get_invoices, get_order_status

#CONSTANTS=========
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

#FUNCTIONS=========
def upload_open_orders(customer_id,shipment_locations,channel):
	#gmap = gmplot.GoogleMapPlotter(42.2121127,-71.5901177, 16).from_geocode("Boston")
	#16 is zoomed in 1 is zoomed out
	gmap = gmplot.GoogleMapPlotter(42.371850, -71.182870, 12)
	#TODO delete old zip and html files
	#TODO zoom to data point lon, lats to properly frame in single view (including customer location); draw customer location
	lats = []
	lons = []
	for shipment in shipment_locations:
		print shipment['lat'] + " " + shipment['lon']
		lats.append(float(shipment['lat']))
		lons.append(float(shipment['lon']))
	gmap.scatter(lats,lons,'#FF0000',size=100,marker=True)
	#gmap.plot(lats,lons,"#FF0000",edge_width=10)
	gmap.draw("customer_orders_map.html")
	zf = zipfile.ZipFile("customer_orders_map.zip", "w")
	zf.write("customer_orders_map.html")
	zf.close()
	os.system("curl -F file=@customer_orders_map.zip -F channels="+channel+" -F token="+SLACK_BOT_TOKEN+" https://slack.com/api/files.upload")

def get_shipment_locations(customer_id):
	invoices = get_invoices(customer_id)
	shipment_locations = []
	for index, invoice in enumerate(invoices):
		order_info = get_order_status(invoice['id'])
		#print status['latitud']
		#print str(index) + " " + status
		if order_info['status'] == "on route":
			obj = {'id':index,
			'lat':order_info['latitud'],
			'lon':order_info['longitud']}
			shipment_locations.append(obj)
	return shipment_locations

#TOTAL SCATTERED RANDOM NOTES TO BE DELETED========

#customer = get_entry("id",customer_id,"customer_list")
#print "Customer Info: " + customer + "\n\n"
#invoices = get_entry('id',customer_id,'customer_invoices',str(customer_id))
#customer_id = get_customer()['id']
#upload_open_orders(customer_id,shipment_locations)