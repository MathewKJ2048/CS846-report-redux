from conf import *
from lib import *


def correlation_analysis():
	# correlate lines of model with lines of summary text
	# correlate lines of model with lines of reconstructed
	dset_recon = get_dataset_reconstructed()
	dset_sum = get_dataset_summary()
	print(len(dset_sum))

	recon_x = []
	recon_y = []
	for i in dset_recon:
		model_text = read_file(i)
		recon_text = get_reconstructed(i)
		if not recon_text:
			continue
		recon_x.append(len(model_text))
		recon_y.append(len(recon_text))
	correlation_scatter_plot(recon_x,recon_y,"number of characters in original","number of characters in reconstruction", "correlation between size of original and reconstructed model")

	sum_x = []
	sum_y = []
	for i in dset_sum:
		model_text = read_file(i)
		think, summary = get_summary(i)
		if not summary:
			continue
		sum_x.append(len(model_text))
		sum_y.append(len(summary))
	correlation_scatter_plot(sum_x,sum_y,"number of characters in model","number of characters in summary", "correlation between size of model and LLM-generated summary")



		

def reconstruction_analysis():

	fields = ["lines","characters","tokens"]
	def get_data(model_text):
		return {
			'lines':len(model_text.split("\n")),
			'characters':len(model_text),
			'tokens':count_tokens(model_text)
		}
	dataset = get_dataset_reconstructed()

	analysis_data_original = []
	analysis_data_reconstructed = []
	for i in dataset:
		modeltext = read_file(i)
		reconstructed = get_reconstructed(i)
		if not reconstructed:
			continue
		analysis_data_original.append(get_data(modeltext))
		analysis_data_reconstructed.append(get_data(reconstructed))
	

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
	dataset = get_dataset_summary()
	ct=0
	for i in dataset:
		try:
			ct+=1
			print(ct/len(dataset))
			thought, text = get_dataset_summary(i)
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


corpus_analysis()
# summary_analysis()
reconstruction_analysis()
correlation_analysis()




