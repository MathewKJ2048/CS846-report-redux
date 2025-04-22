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

i = 0
for p in index:
	try:
		i+=1
		print(i/len(index))
		text = read_file(p)
		number_of_lines.append(len(text.split("\n")))
		number_of_characters.append(len(text))
		number_of_tokens.append(count_tokens(text))
	except:
		pass


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

generate_histogram(number_of_characters,"Number of characters, distribution in corpus")
generate_histogram(number_of_lines,"Number of lines, distribution in corpus")
generate_histogram(number_of_tokens,"Number of tokens, distribution in corpus")