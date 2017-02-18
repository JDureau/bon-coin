# -*- coding: utf-8 -*-
import os
import urllib
from unidecode import unidecode
import requests
import json
import math

only_unseen_houses=True

# ATTENTION: pas d'accents!!!!
all_cities=[
	"La Riche 37520",
	"Joue-les-Tours 37300",
	"Ballan-Mire 37510",
	"Saint-Cyr-sur-Loire 37540",
	"La Membrolle-sur-Choisille 37390",
	"Saint-Pierre-des-Corps 37700",
	"Chambray-les-Tours 37170"
]

parameters={
	"nombre_de_pieces_min": 4, #ros
	"nombre_de_pieces_max": 6, #roe 
	"prix_min": 75000, #ps
	"prix_max": 150000, #pe
	"surface_min":50, #sqs
	"surface_max":100 #sqe
}






def pick_index(parameter,parameters,options_per_parameter):
	value=parameters[parameter]
	options=options_per_parameter[parameter]

	if value not in options:
		raise ValueError("Pour {0}, choisir une des options suivantes: {1}".format(parameter, options))

	return options.index(value)


def encode_parameters(parameters):
	
	room_options=[1,2,3,4,5,6,7,8]
	price_options=[0,25000,50000,75000,100000,125000,150000,175000,200000,225000,250000]
	surface_options=[0,20,25,30,35,40,50,60,70,80,90,100,110,120,130,140,150,200,300]


	options_per_parameter={
		"nombre_de_pieces_min": room_options,
		"nombre_de_pieces_max": room_options,
		"prix_min": price_options,
		"prix_max": price_options,
		"surface_min": surface_options,
		"surface_max": surface_options
	}

	code_per_parameter={
		"nombre_de_pieces_min": "ros",
		"nombre_de_pieces_max": "roe",
		"prix_min": "ps",
		"prix_max": "pe",
		"surface_min": "sqs",
		"surface_max": "sqe"
	}


	encoded_parameters={}

	for parameter in options_per_parameter.keys():
		index=pick_index(parameter,parameters,options_per_parameter)
		encoded_parameters[code_per_parameter[parameter]]=index

	return encoded_parameters
	

def generate_url(encoded_parameters,cities):
	url="https://www.leboncoin.fr/ventes_immobilieres/offres/centre/?th=1"
	url+="&location={0}&".format(urllib.quote((",".join(cities)).encode("utf-8")))
	url+="&".join(["{0}={1}".format(urllib.quote(k),urllib.quote(str(v))) for (k,v) in encoded_parameters.iteritems()])
	url+="&ret=1" #maison
	return url


def extract_house_urls(text):
	remaining_text=text
	extracted_urls=[]
	while 'href' in remaining_text:
		start=remaining_text.index('href')+8
		remaining_text=remaining_text[start:]
		end=remaining_text.index('"')
		potential_url=remaining_text[:end]
		if "ventes_immobilieres" in potential_url and "ca=7_s" in potential_url:
			extracted_urls.append(potential_url)
	return extracted_urls


def detect_unseen_urls_and_update_db(extracted_urls):
	with open('record.json') as data_file:    
		record = json.load(data_file)
	unseen_urls=[]
	for url in extracted_urls:
		if only_unseen_houses:
			if url not in record:
				unseen_urls.append(url)
		else:
			unseen_urls.append(url)
		if url not in record:
			record.append(url)
	with open('record.json', 'w') as outfile:
	    json.dump(record, outfile)
	return unseen_urls

def open_urls(urls):
	for url in urls:
		os.system('python -m webbrowser -t "https://{0}"'.format(url))

if __name__ == '__main__':

	for i in range(int(math.ceil(len(all_cities)/3.0))):
		cities=all_cities[i*3:(i+1)*3]
		print cities
		url=generate_url(encode_parameters(parameters), cities)
		extracted_urls=extract_house_urls(requests.get(url).text)
		unseen_urls=detect_unseen_urls_and_update_db(extracted_urls)
		open_urls(unseen_urls)


