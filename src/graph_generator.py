from conf import *
from lib import *

def get_subgraph(label,code,color):
	root = Node.decode(code)
	assert root!=None
	node_list = []
	def get_list(n):
		node_list.append(n)
		for c in n.children:
			get_list(c)
	get_list(root)

	for i in range(len(node_list)):
		node_list[i].representation = "n"+label+"_"+str(i)


	sfull = "\nsubgraph cluster_"+label+" {"
	sfull+= "\nlabel=\""+label+"\";\n"
	sfull+= "\nstyle = \"rounded\";"
	sfull+= "\nnode [style=\"rounded,filled\",fillcolor=\""+color+"\"];"


	for n in node_list:
		s = "\n"+n.representation+" [label=\"\"];"
		for c in n.children:
			s+="\n"+n.representation+" -> "+c.representation+";"
		sfull+=s
	return sfull+"\n}"

def get_graph(codelist,colorlist):
	s = "digraph rootgraph {\n rankdir=TB;\ncompund=true;\n"
	for i in range(len(codelist)):
		s+=get_subgraph(str(i),codelist[i],colorlist[i])
	print(s)
	return s+"\n}"


