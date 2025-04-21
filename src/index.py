from conf import *


def extract_first(di):
	k = list(di.keys())[0]
	return k

def make_index():

	FILENAMES = {}

	for root, dirs, files in os.walk(CORPUS_FOLDER):
		for f in files:
			if not f.endswith(".als"):
				continue
			FILENAMES[os.path.join(root,f)] = {}

	total_out=0
	error_out=0
	for root, dirs, files in os.walk(OUT_FOLDER):
		for f in files:
			fn = os.path.join(root,f)
			with open(fn) as fi:
				data = eval(fi.read())
			fkey = extract_first(data)
			out_data = data[fkey]
			llm_name = extract_first(out_data)
			f_index_key = CORPUS_FOLDER+fkey[8:]
			if f_index_key in FILENAMES:
				FILENAMES[f_index_key][llm_name] = fn
			else:
				error_out+=1
			total_out+=1

	total_models=0
	error_models=0
	for root, dirs, files in os.walk(MODELS_FOLDER):
		for f in files:
			fn = os.path.join(root,f)
			with open(fn) as fi:
				data = eval(fi.read())
			fkey = extract_first(data)
			out_data = data[fkey]
			llm_name = extract_first(out_data)
			f_index_key = CORPUS_FOLDER+fkey[8:]
			if f_index_key in FILENAMES:
				FILENAMES[f_index_key][llm_name] = fn
			else:
				error_models+=1
			total_models+=1
			
				

	print("total alloy files: "+str(len(FILENAMES)))
	print("total number of summaries: "+str(total_out))
	print("total number of reconstructed models: "+str(total_models))
	print("percentage of unidentified summary files: "+str(100*error_out/total_out))
	print("percentage of unidentified reconstructed model files: "+str(100*error_models/total_models))

	with open("./out/index.json","w") as index_file:
		json.dump(FILENAMES,index_file)


