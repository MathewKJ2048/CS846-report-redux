from conf import *
from lib import *
from graph_generator import *

test_model = """
module language/grandpa1 ---- Page 84, 85

// a sig declares a set of atoms, with shared properties
abstract sig Person {
	father: lone Man, // lone is a condition on multiplicity, this means that every Person p has exactly one Man m as p.father
	mother: lone Woman
	}

sig Man extends Person {
	// Man inherits all the properties of Person, with additional properties
	wife: lone Woman
	}

sig Woman extends Person {
	husband: lone Man
	}

fact {
	// a fact is a condition on the possible relations between atoms
	no p: Person | p in p.^(mother+father)
	wife = ~husband
	}

assert NoSelfFather {
	// assertions are claims about the relations between atoms, which are not necessarily true. They may be true as a consequence of the definitions of the sigs and facts, which is determined by the Analyzer
	no m: Man | m = m.father
	}

// This should not find any counterexample.
check NoSelfFather

fun grandpas [p: Person] : set Person {
	// fun f [a: T]: U takes an argument of type T and returns something of type U
	p.(mother+father).father
	}

pred ownGrandpa [p: Person] {
	// a function that returns a boolean value
	p in p.grandpas
	}

// This should not find any instance.
run ownGrandpa for 4 Person

assert NoSelfGrandpa {
	no p: Person | p in p.grandpas
	}

// This should not find any counterexample
check NoSelfGrandpa for 4 Person

"""

def parse(model_text):
	comments = get_comments(model_text)
	model_text = re.sub(r"\/\/[^\n]*\n","\n",model_text)
	model_text = enspacify(model_text)
	
	return {
		"comments":comments, 
		"sigs":get_sigs(model_text),
		"funs":get_elements("fun",model_text),
		"preds":get_elements("pred",model_text),
		"facts":get_elements("fact",model_text),
		"asserts":get_elements("assert",model_text)
	}


def generate_tree(signature_list):
	name_list = {}

	# put strings as keys, blank nodes
	for s in signature_list:
		name_list[s.name] = Node()
		if s.parent:
			name_list[s.parent] = Node()

	# solidify parentage
	for s in signature_list:
		s_node = name_list[s.name]
		if s.parent:
			p_node = name_list[s.parent]
			p_node.children.append(s_node)
			s_node.parent = p_node

	# convert forest to single tree
	phantom = Node()
	for name in name_list:
		s = name_list[name]
		if not s.parent:
			s.parent = phantom
			phantom.children.append(s)
	return phantom


class Element:
	def __init__(self, text, is_fact=False):
		if is_fact:
			m = re.search(r"fact ({[^{}]*})",text)
			self.body = m.group(1)
			self.type = "fact"
			self.name = ""
			self.header = ""
			return
		m = re.search(r"([^ ]+) ([^ ]+) ([^{}]*)({[^{}]*})",text)
		self.type = m.group(1)
		self.name = m.group(2)
		self.header = m.group(3)
		self.body = m.group(4)
	def stringify(self):
		s = "type:"+self.type+"\n"
		s += "name:"+self.name+"\n"
		s += "header:"+self.header+"\n"
		s += "body:"+self.body+"\n"
		return s

class Signature:
	def __init__(self,text):
		m = re.search(r"sig ([^ ]*) ([^{}]*)({[^{}]*})",text)
		self.name = m.group(1)
		modifier = m.group(2)
		self.abstract = ("abstract" in text)
		self.body = m.group(3)
		self.parent = None
		m = re.search(r"extends ([^ ]*)",modifier)
		if m:
			self.parent = m.group(1)
	def stringify(self):
		s = "abstract:"+str(self.abstract)+"\n"
		s+="name:"+self.name+"\n"
		s+="body:"+self.body+"\n"
		s+="parent:"+str(self.parent)
		return s


def get_sigs(model_text):
	sigs = re.findall(r"(?:abstract)? sig [^ ]* [^{}]*{[^{}]*}",model_text)
	return [Signature(s) for s in sigs]

def get_elements(element_type,model_text):
	if element_type == "fact":
		els = re.findall(element_type+r" {[^{}]*}",model_text)
		return [Element(e,is_fact=True) for e in els]
	els = re.findall(element_type+r" [^ ]* [^{}]*{[^{}]*}",model_text)
	return [Element(e) for e in els]

def get_comments(model_text):
	model_text+=("\n")
	comments = re.findall(r"\/\/[^\n]*\n",model_text)
	return [c[2:-1] for c in comments]


def comparative_corelation_analysis(func,quantity):
	dset = get_dataset_reconstructed()
	original_dataset = []
	recons_dataset = []
	for i in dset:
		model_text = read_file(i)
		recon_text = get_reconstructed(i)
		if not recon_text:
			continue
		original_als = parse(model_text)
		recons_als = parse(recon_text)
		original_dataset.append(func(original_als))
		recons_dataset.append(func(recons_als))
	print(len(original_dataset))
	correlation_scatter_plot(original_dataset,recons_dataset,
	quantity+" in original models",quantity+" in reconstructed models","Correlation between "+quantity+" in the original and reconstructed models")


def comparative_distribution_analysis(func,quantity):
	dset = get_dataset_reconstructed()
	original_dataset = []
	recons_dataset = []
	for i in dset:
		model_text = read_file(i)
		recon_text = get_reconstructed(i)
		if not recon_text:
			continue
		original_als = parse(model_text)
		recons_als = parse(recon_text)
		if type(func(original_als)) == list:
			original_dataset+=(func(original_als))
			recons_dataset+=(func(recons_als))
		else:
			original_dataset.append(func(original_als))
			recons_dataset.append(func(recons_als))
	
	print(len(original_dataset)/len(dset))
	
	generate_histograms(
			[original_dataset,recons_dataset],
			['original','reconstructed'],
			"Comparing "+quantity+" in the corpus vs the reconstructed models")

def comment_analysis():
	def get_comment_number(parse_data):
		return len(parse_data["comments"])
	def total_comment_size_words(parse_data):
		return sum([len(c.split(" ")) for c in parse_data["comments"]])
	comparative_distribution_analysis(get_comment_number,"number of comments")
	comparative_distribution_analysis(total_comment_size_words,"total number of words in the comments")

def signature_preliminary_analysis():
	def number(parse_data):
		return len(parse_data["sigs"])
	def size(parse_data):
		return [len(s.body) for s in parse_data["sigs"]]
	comparative_distribution_analysis(number,"number of signatures")
	comparative_distribution_analysis(size,"size of the signature bodies")
	comparative_corelation_analysis(number,"number of signatures")

def general_element_preliminary_analysis():
	elements = ["funs","preds","facts","asserts"]
	def number_function_generator(element_type):
		def number(parse_data):
			return len(parse_data[element_type])
		return number
	for e in elements:
		comparative_distribution_analysis(number_function_generator(e),"number of "+e)
		comparative_corelation_analysis(number_function_generator(e),"number of "+e)




	




def corpus_signature_structural_analysis():
	codes = {}
	ct = 0
	for i in index:
		ct+=1
		print(ct/len(index))
		try:
			model = read_file(i)
			slist = parse(model)["sigs"]
			code = generate_tree(slist).encode()
			if code not in codes:
				codes[code]=0
			codes[code]+=1
		except:
			pass
	signature_structural_analysis_aux(codes,"distribution of inheritance hierarchies (original)")

def reconstructed_signature_structural_analysis():
	codes = {}
	ct = 0
	dset = get_dataset_reconstructed()
	for i in dset:
		ct+=1
		print(ct/len(index))
		try:
			model = get_reconstructed(i)
			if not model:
				continue
			slist = parse(model)["sigs"]
			code = generate_tree(slist).encode()
			if code not in codes:
				codes[code]=0
			codes[code]+=1
		except:
			pass
	signature_structural_analysis_aux(codes,"distribution of inheritance hierarchies (reconstructed)")


def signature_structural_analysis_aux(codes,title):
	plt.clf()
	colorlist = ["#ff0000","#00ff00","#0000ff","#ffff00","#ff00ff","#00ffff"]
	N = len(colorlist)
	codelist_full = list(codes.keys())
	def sortkey(x):
		return -codes[x]
	codelist_full.sort(key=sortkey)
	codelist = codelist_full[:N]

	total = sum([codes[t] for t in codelist_full])
	percentage_list = [codes[c]/total for c in codelist]
	labels = [str(i) for i in range(len(codelist))]

	labels.append("others")
	percentage_list.append(1-sum(percentage_list))	
	colorlist.append("#888888")

	plt.pie(
		percentage_list,
		labels = labels,
		colors = colorlist,
		autopct='%1.1f%%'
	)	
	# plt.title(title)
	plt.savefig(title)

	path = "./out/"+title+".dot"
	with open(path,"w") as fil:
		fil.write(get_graph(codelist,colorlist[:-1]))
	
	os.system("clear")
	command = "dot -Tsvg \""+path+"\" -o \""+path.replace(".dot",".svg")+"\""
	os.system(command)
		
"""
p = parse(test_model)
for x in p:
	print(x)
	try:
		for t in p[x]:
			print(t.stringify())
	except:
		pass
"""


comment_analysis()
signature_preliminary_analysis()
general_element_preliminary_analysis()
corpus_signature_structural_analysis()
reconstructed_signature_structural_analysis()