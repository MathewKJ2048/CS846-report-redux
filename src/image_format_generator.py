import os

names = os.listdir()

pic_names = [n for n in names if n.endswith(".png")]



with open("./README.md") as f:
	documentation = f.read()
documentation = documentation.replace("%20"," ")

pic_names.sort(key=lambda t: documentation.find(t))


template = """
\\begin\{figure\}[htbp]
\centerline{\includegraphics[width=\linewidth]{"./Distribution of ratings from manual analysis.png"}}
\caption{Distribution of ratings from manual analysis.}
\label{fig}
\end{figure}
"""

def construct(filename):
	caption = filename[:-3]
	return "\\begin{figure}[htbp]\n"+"\centerline{\includegraphics[width=\linewidth]{\"./"+filename+"\"}}\n"+"\caption{"+caption+"}\n"+"\label{fig}\n"+"\end{figure}\n"




output = ""

for p in pic_names:
	output+="\n\n"+construct(p)

with open("./out/pic_index.tex","w") as f:
	f.write(output)
