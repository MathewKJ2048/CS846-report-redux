from conf import *
from lib import *

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
		"sigs":get_sigs(model_text)
	}

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
	signatures = []
	for s in sigs:
		signatures.append(Signature(s))
	return signatures

def get_comments(model_text):
	model_text+=("\n")
	comments = re.findall(r"\/\/[^\n]*\n",model_text)
	return [c[2:-1] for c in comments]



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

comment_analysis()


