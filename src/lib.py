import os
import sys
import json
import math
import re
import matplotlib.pyplot as plt
from conf import *


def enspacify(text):
	text = text.replace("\n"," ")
	text = text.replace("\t"," ")
	text = text.replace("\r"," ")
	return text

def count_tokens(text):
		text = enspacify(text)
		return len(text.split(" "))

def extract_code(text):
	m = re.search(r"```(.*)```",text,re.DOTALL)
	if m:
		return m.group(1)
	return None

def extract_thoughts(text):
	m = re.search(r"<think>([^<]*)</think>",text,re.DOTALL)

def extract_first(di):
	k = list(di.keys())[0]
	return k

def read_file(path):
	with open(path) as f:
		data = f.read()
	if path.endswith(".stream"):
		data = eval(data)
		data = data[extract_first(data)]
		data = data[extract_first(data)]
		assert type(data) == str
	return data

def get_index():
	PATH = ("./out/index.json")
	with open(PATH) as f:
		return json.load(f)

def process_response(path):
	data = read_file(path)
	result = {
		"think":None,
		"code":None,
		"text":None
	}
	try:
		m = re.search(r"<think>([^>]*)</think>(.*)",data,re.DOTALL)
		result["think"] = m.group(1)
		result["text"] = m.group(2)
		m = re.search(r"```(.*)```",result["text"],re.DOTALL)
		result["code"] = m.group(1)
	except:
		pass
	return result


index = get_index()

sub_index = list(index.keys())[:1000]


def get_dataset_summary():
	dataset = []
	for i in index:
		if LLM_NAME+"(summary)" in list(index[i].keys()):
			dataset.append(i)
	return dataset

def get_dataset_reconstructed():
	dataset = []
	for i in index:
		if LLM_NAME+"(reconstruction)" in list(index[i].keys()):
			dataset.append(i)
	return dataset

def get_reconstructed(i):
	return process_response(index[i][LLM_NAME+"(reconstruction)"])["code"]

def get_summary(i):
	response = process_response(index[i][LLM_NAME+"(summary)"])
	thought = response["think"]
	text = response["text"]
	return thought, text


def generate_histogram(data,title):
	base = 2  # Change base if desired (e.g., 10 for decades)
	max_power = int(math.log2(max(data))) + 1  # Adjust to cover data range
	bins = [base**i for i in range(max_power + 1)]  # Power-law bins
	plt.clf()
	plt.hist(data, bins=bins, edgecolor='black', alpha=0.7)
	plt.yscale('log')
	plt.xscale('log')
	plt.xlabel('Number (logarithmic bins)')
	plt.ylabel('Frequency (log scale)')
	plt.title('Histogram with Power-Law Bins and Log Y-Axis')
	plt.grid(True, which="both", ls="--", alpha=0.3)
	plt.title(title)
	plt.savefig(title)

def generate_histograms(data,legend,title):
	base = 2  # Change base if desired (e.g., 10 for decades)
	max_power = int(math.log2(max([max(d) for d in data]))) + 1  # Adjust to cover data range
	bins = [base**i for i in range(max_power + 1)]  # Power-law bins
	plt.clf()
	for i in range(len(data)):
		plt.hist(data[i], bins=bins, edgecolor='black', alpha=0.7,label=legend[i])
	plt.yscale('log')
	plt.xscale('log')
	plt.xlabel('Number (logarithmic bins)')
	plt.ylabel('Frequency (log scale)')
	plt.title('Histogram with Power-Law Bins and Log Y-Axis')
	plt.grid(True, which="both", ls="--", alpha=0.3)
	plt.legend()
	plt.title(title)
	plt.savefig(title)




def correlation_scatter_plot(x_data,y_data,xv,yv,title):

	plt.clf()
	plt.scatter(x_data, y_data, color='blue', alpha=0.7, edgecolors='w', s=100)

	# Set logarithmic scales for both axes
	plt.xscale('log')
	plt.yscale('log')

	# Add labels and title
	plt.xlabel(xv+' (log scale)', fontsize=12)
	plt.ylabel(yv+' (log scale)', fontsize=12)
	plt.title('Scatter Plot of Correlation between '+xv+" and "+yv, fontsize=14)
	plt.grid(True)
	plt.title(title)
	plt.savefig(title)