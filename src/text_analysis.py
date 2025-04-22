from conf import *
from lib import *


index = get_index()

sub_index = list(index.keys())[:1000]


def enspacify(text):
	text = text.replace("\n"," ")
	text = text.replace("\t"," ")
	text = text.replace("\r"," ")
	return text

def summary_analysis():
	number_of_words_s = []
	number_of_sentences_s = []
	number_of_words_t = []
	number_of_sentences_t = []
	dataset = []
	for i in index:
		if index[i] is not {}:
			dataset.append(i)
	ct=0
	for i in dataset:
		try:
			ct+=1
			print(ct/len(dataset))
			if index[i] is not {}:
				response = process_response(index[i][LLM_NAME+"(summary)"])
				thought = response["think"]
				text = response["text"]
				number_of_sentences_s.append(len(text.split(".")))
				number_of_words_s.append(len(text.split(" ")))
				number_of_sentences_t.append(len(thought.split(".")))
				number_of_words_t.append(len(thought.split(" ")))
		except:
			pass
	
	generate_histogram(number_of_sentences_s,"Number of sentences in summary")
	generate_histogram(number_of_words_s,"Number of words in summary")
	generate_histogram(number_of_sentences_t,"Number of sentences in <think> section")
	generate_histogram(number_of_words_t,"Number of words in <think> section")

	

def corpus_analysis():
	number_of_lines = []
	number_of_characters = []
	number_of_tokens = []

	def count_tokens(text):
		text = enspacify(text)
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

	generate_histogram(number_of_characters,"Number of characters, distribution in corpus")
	generate_histogram(number_of_lines,"Number of lines, distribution in corpus")
	generate_histogram(number_of_tokens,"Number of tokens, distribution in corpus")


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

