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


def manual_analysis_main():
	# table is structured as follows:
	# keys are file_names
	# objecs are lists
	# each element is of the form:
	# ratings: absent, incorrect, correct, indeterminate
	"""
	{
		"type":
		"name":
		"rating":
	}
	"""
	with open("./out/table.json") as f:
		table = json.load(f)

	with open("./out/curated_index.json") as f:
		curated_index = json.load(f)["set"]

	remaining_index = []
	for c in curated_index:
		if c in table:
			continue
		remaining_index.append(c)

	for i in remaining_index:
		model_text = read_file(i)
		summary_think, summary_text = get_summary(i)
		if type(summary_text)!=str:
			print("A")
		with open("./out/model_text.temp","w") as f:
			f.write(model_text)
		with open("./out/summary.md","w") as f:
			f.write(str(summary_text))
		table[i] = []
		p = parse(model_text)
		for t in ["sigs","funs","preds","asserts"]:
			for s in p[t]:
				os.system("clear")
				print(len(remaining_index))
				print(t)
				print(s.name)
				print("1 - absent\n2 - incorrect\n3 - correct\n4 - indeterminate")
				ch = input()
				RAT = "PROBLEM"
				if ch == "1":
					RAT = "absent"
				elif ch == "2":
					RAT = "incorrect"
				elif ch == "3":
					RAT = "correct"
				elif ch == "4":
					RAT = "indeterminate"
				table[i].append({"name":s.name,"type":t,"rating":RAT})

		with open("./out/table.json","w") as f:
			json.dump(table,f)
	
	print(len(remaining_index))



manual_analysis_main()


