from conf import *
from lib import *




index = get_index()

sub_index = list(index.keys())[:1000]




def reconstruction_analysis():

	fields = ["lines","characters","tokens"]
	def get_data(model_text):
		return {
			'lines':len(model_text.split(" ")),
			'characters':len(model_text),
			'tokens':count_tokens(model_text)
		}
	dataset = []
	for i in index:
		if len(index[i]) == 2:
			dataset.append(i)

	analysis_data_original = []
	analysis_data_reconstructed = []
	for i in dataset:
		modeltext = read_file(i)
		response = process_response(index[i][LLM_NAME+"(reconstruction)"])
		if not response["code"]:
			continue
		analysis_data_original.append(get_data(modeltext))
		analysis_data_reconstructed.append(get_data(response["code"]))
	

	def generate_graph(field):
		generate_histograms(
			[[d[field] for d in analysis_data_original],
			[d[field] for d in analysis_data_reconstructed]],
			['original','reconstructed'],
			"Comparing number of "+field+" in the corpus vs the reconstructed models")

	for f in fields:
		generate_graph(f)



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


