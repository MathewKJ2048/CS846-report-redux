import os
import sys
import json
import re
import matplotlib.pyplot as plt


def extract_code(text):
	m = re.search(r"```(.*)```",text,re.DOTALL)
	if m:
		return m.group(1)
	return None

def extract_thoughts(text):
	m = re.search(r"<think>([^<]*)</think>",text,re.DOTALL)

def read_file(path):
	with open(path) as f:
		data = f.read()
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
