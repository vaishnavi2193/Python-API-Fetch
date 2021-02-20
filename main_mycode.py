import csv
import hmac
import hashlib
import base64
import requests

AUTH_ID = '<API-ID>'
AUTH_KEY = '<API-KEY>'

def get_pages(url, header):
	''' Get the number of pages available '''
	return requests.get(url, headers = header).json()['Pagination']['NumberOfPages']

def getSignature(args, privateKey):
	''' Create a HMAC-SHA256 signature as per API Specs '''
	key = str.encode(privateKey, encoding='ASCII')
	msg = str.encode(args, encoding='ASCII')
	myhmacsha256 = hmac.new(key, msg, digestmod=hashlib.sha256).digest()
	return base64.b64encode(myhmacsha256).decode()

def get_resource(resource_name, kwargs={}):
	''' Download using unleashed API '''
	print('Downloading %s Data' % resource_name)

	url = f'https://api.unleashedsoftware.com/{resource_name}'

	# Create Header as per https://apidocs.unleashedsoftware.com/AuthenticationHelp
	header = {
		'api-auth-id': AUTH_ID,
		'api-auth-signature': getSignature('', AUTH_KEY),
		'Accept': 'application/json',
		'Content-Type': 'application/json',
	} 

	# Get Number of pages and grab data for each page, then merge results together
	pages = get_pages(url, header)
	results = []
	for i in range(1, pages + 1):
		url = f'https://api.unleashedsoftware.com/{resource_name}/{i}'
		r = requests.get(url, headers = header).json()['Items']
		for result in r:
			results.append(result)
	return results


def write_to_csv(csv_file, data, text):
	''' Write data to csv files '''
	print('Saving %s Results...' % text)
	try:
		with open(csv_file, 'w', newline='') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
			writer.writeheader()
			for row in data:
				writer.writerow(row)
	except IOError:
		print("I/O error")


customers = get_resource('Customers')
write_to_csv('customers.csv', customers, 'Customers')

invoices = get_resource('Invoices')
write_to_csv('invoices.csv', invoices, 'Invoices')

print('Done!')