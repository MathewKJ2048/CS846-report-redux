from conf import *
from lib import *
from semantic_analysis import *


def filtered_index():

	
	dset = get_dataset_summary()

	minimum_size = 10
	maximum_size = 100

	dest_filtered = []

	for i in dset:
		model_text = read_file(i)
		number_of_lines = len(model_text.split("\n"))
		if number_of_lines < maximum_size and number_of_lines > minimum_size:
			dest_filtered.append(i)

	dset_hyperfiltered = []
	text_hyperfiltered = []

	ct=0
	for i in dest_filtered:
		ct+=1
		print(ct/len(dest_filtered))
		model_text = read_file(i)
		unique = True
		for t in text_hyperfiltered:
			if common(t,model_text)>0.5:
				unique = False
				break
		if unique:
			dset_hyperfiltered.append(i)
			text_hyperfiltered.append(model_text)
	
	with open("./out/filtered_index.json","w") as f:
		json.dump({"set":dset_hyperfiltered},f)



# filtered_index()


def make_set():

	with open("./out/filtered_index.json") as f:
		dest_filtered = json.load(f)["set"]

	curated_set = []
	for t in range(len(dest_filtered)):
		i = dest_filtered[t]
		with open("./out/temp","w") as f:
			model_text = read_file(i)

		os.system("clear")
		print(model_text)
		print("----------------------------------------------------------")
		print(str(len(curated_set))+" chosen far")
		print("model index"+str(t)+" out of"+str(len(dest_filtered)))

		ch = input()
		if len(ch)!=0:
			curated_set.append(i)

		with open("./out/curated_index.json","w") as f:
			json.dump({"set":curated_set},f)


make_set()