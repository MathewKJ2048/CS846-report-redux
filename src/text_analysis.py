from conf import *
from lib import *


index = get_index()

sub_index = list(index.keys())[:1000]

number_of_lines = []
number_of_characters = []
number_of_tokens = []

def count_tokens(text):
	text.replace("\n"," ")
	text.replace("\t"," ")
	text.replace("\r"," ")
	return len(text.split(" "))

for p in sub_index:
	try:
		text = read_file(p)
		number_of_lines.append(len(text.split("\n")))
		number_of_characters.append(len(text))
		number_of_tokens.append(count_tokens(text))
	except:
		pass

print(number_of_characters)

