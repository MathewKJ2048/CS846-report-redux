# CS846 project report - Applying LLMs to Alloy models

## Abstract

## CCS concepts

- LLM: Large Language Model
- deepseek: specific open-weight LLM
- Alloy: formal declarative specification language
- model: self-contained unit of Alloy code
- AST: Abstract Syntax Tree


## Introduction

### Declarative modelling and Alloy



Software modeling is an important part of software development, used for managing complexity and ensuring correctness [cite].


Alloy is a formal declarative specification language, for expressing structural constraints and behaviour.


The following example is from Jackson's Software Abstractions, with added annotations:

```
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

```

This is a simple model of a familial structure, which asserts that no `Person` p can be their own grandfather or their own father. 

Properties of more complex systems can be modelled similarly, after which the Alloy Analyzer is used to look for counterexamples to assertions about the model's properties.


### LLMs and deepseek

A large language model (LLM) is a machine learning model designed for natural language processing, such as language and code generation. LLMs are trained on a vast corpus of existing examples of text, and can be used to produce new examples of the text. When combined with a prompt, the LLM follows instructions in a manner similar to a chatbot.


Mixture of Experts (MoE) is a machine learning technique where learners operate on the same input, with their outputs combined by a weighting function, to produce a single output.

DeepSeek is a MoE LLM released as an open-weight model. An open-weight model can be run by anyone on their own hardware, as opposed to closed-weight LLMs like Chat-GPT, which can be accesed only via an API. 

The research questions of this project are:

1) Given an Alloy model, how well can deepseek summarize the model in plain english?

2) Can deepseek write valid Alloy models?

2) Given a summary of a model in plain english, how well can deepseek capture the requirements when it constructs the model in Alloy?

The results shed light on LLMs' ability to comprehend and use declarative modelling languages, which could increase the adoption of software modelling in the industry. Since a significant hurdle to the adoption of tools such as Alloy in production is the unfamiliarity of the developers with declarative modelling, the introduction of AI-assisted creation of models may increase the use of Alloy and similar tools (TLA+, Z, B etc.) in software development.

When the earlier example model is fed into deepseek with a request for a summary, the following is produced:

```
This Alloy module defines a family relationship structure and enforces constraints to prevent impossible genealogical cycles (e.g., someone being their own grandfather).
Key Components

    Signatures (sig)

        abstract sig Person: Base type with optional father (Man) and mother (Woman).

        sig Man extends Person: Adds wife (lone Woman).

        sig Woman extends Person: Adds husband (lone Man).

    Constraints (fact)

        No cycles: no p: Person | p in p.^(mother+father) (no person is their own ancestor).

        Spouse symmetry: wife = ~husband (wife/husband are mutual).

    Functions & Predicates

        grandpas[p: Person]: Returns a person’s grandfathers (mother/father → father).

        ownGrandpa[p: Person]: Checks if someone is their own grandpa (impossible by design).

    Verification

        Assertions:

            NoSelfFather: No man is his own father.

            NoSelfGrandpa: No person is their own grandpa.

        Checks:

            check NoSelfFather / check NoSelfGrandpa: Verify assertions hold.

            run ownGrandpa for 4: Confirms no valid instance exists.

Purpo
se

    Model family trees without contradictions.

    Ensure logical consistency (e.g., no time-traveling grandparents).

The Analyzer confirms all constraints are satisfied.

Want to extend this? For example, add siblings or marriages between cousins?

```


## Methodology

### Data collection

![alt_image](./images/scraping.svg)

The primary data source for Alloy models is GitHub, whose public repositories with `.als` files are scraped by a script. After scraping, the files are passed through a filter which determines the file type, before moving the files to local storage.

Given a corpus of `.als` files containing Alloy code, the version of Alloy is determined via a simple check of the keywords used. Alloy 6 is not back-compatible with earlier versions of Alloy, and is characterized by the following keywords (which do not appear in Alloy 5 code):

```
keywords = "after always before enabled event eventually historically invariant modifies once releases since steps triggered until var".split(" ")
```

Determining the version is carried out by a simple algorithm shown below:

```
def remove_strings(text):
	text = remove_escape_sq(text)
	text = re.sub(r"\"[^\"]*\"","",text,re.DOTALL)
	return text

def check_presence(text):
	text = remove_strings(text)
	text.replace("\n"," ")
	text.replace("\t"," ")
	text.replace("\r"," ")
	for k in keywords:
		if " "+k+" " in text:
			return True
	return False
```

Alloy strings are enclosed in double quotes (`"`). Before checking for the presence of keywords, the string literals are eliminated via a regular expression, since a simple word search will match all occurances of the Alloy-6 keywords, even if they are part of a string literal (which is semantically distinct from occurance in the code). The Alloy version is inserted as a comment at the top of the model code, as:

```
// This is an Alloy 6 model
```

for models whose version is confirmed to be Alloy 6. No modification is done to models which could be interpreted as either Alloy 5 or Alloy 6.

### Invoking the LLM:

Engineering a pipeline to extract data automatically from LLMs has the following requirements:

1) Stability - if a process crashes, the data loss should be minimal.

2) Parallelizability - the pipeline should be easy to expand to run on multiple machines, without relying on interprocess communication between machines.

3) Reproducibility - Since LLMs are stochastic, the results produced are pseudorandom. For independent verification, the results must be reproducible.

![](./images/process.png)

The control script reads a file, constructs the prompt from the file, and feeds it into the LLM. The seed is set to be 0, for reproducibility. The output is stored in a `.stream` file, which consists of the following metadata in addition to the response:

1) The generation timestamp (unix epoch)
2) An index which points to the file from which the prompt was generated

After each response generation, a `.stream` file is created and stored in permanent storage. This ensures that if the process crashes:

1) All data stored thus far is saved (except the response being generated during the crash).
2) The process can be recovered by reading the indices of the generating files in the `.stream` file, which allows it to continue with unprocessed files.
3) A real-time alert can be generated for crashes by a separate process that continuously scans the timestamps of the existing `.stream` files and raising an alert if there is a large difference between the current time and the timestamp of the last generated file.

### Prompt engineering

![](./images/pipeline.svg)

In accordance with the standard best pracitces for prompt engineering, the following was done:

1) The instructions were appended to the beginning of the prompt, to ensure that sufficient attention was allocated to the instruction.

2) The context was clearly separated from the instructions, so the line between the where the instructions to the LLM ends and the model to analyze begins is clear.

The two prepended instructions are:

```
"This is sample Alloy code. Provide an accurate summary of the code, make it as detailed as possible\n"
```

```
"Here is a summary of an Alloy model in plain english. Generate the Alloy code:"+summary+"\n Provide only Alloy code, not a summary"
```

For the second experiment (the generation of the code from the prompt), about 91% of the queries resulted in Alloy code. The presence of code in the response was identified by looking for the presence of "```" in the response, which is used to indicate code segments.

The general structure of a response by deepseek is:

```
<think>
(internal thoughts)
</think>
(explanation)
'''
(code)
'''
(summary of explanation)
```

The constituent parts of the response a separated out via matching using regular expressions.

## Results

### Analysis of the corpus

Initial analysis of the corpus consists of examining simple characteristics like the number of lines, number of tokens and number of characters.

![](./Number%20of%20characters,%20distribution%20in%20corpus.png)

![](./Number%20of%20lines,%20distribution%20in%20corpus.png)

![](./Number%20of%20tokens,%20distribution%20in%20corpus.png)

When examining the number of lines, there seems to be a large number of `.als` files with very few lines (which could be because of a large number of empty or very small models in the corpus).

A similar analysis is carried out for the number of words and sentences in the summaries generated by deepseek. The data is split based on the actual summary and the 'think' section, which shows deepseek's reasoning.

![](./Number%20of%20sentences%20in%20summary.png)

![](./Number%20of%20sentences%20in%20<think>%20section.png)


![](./Number%20of%20words%20in%20summary.png)

![](./Number%20of%20words%20in%20<think>%20section.png)

The relative sharpness of the distribution peaks for the responses, in comparison to the distributions for the original model, show that deepseek tends to have a fairly limited response window size.

Further investigation of the relationship between the size of the model being summarized and the size of the summary is shown below:

![](./Comparing%20number%20of%20characters%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Comparing%20number%20of%20lines%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Comparing%20number%20of%20tokens%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

From the data, it is clear that the LLM is capable of producing models whose length is at or below the mode for the dataset. However, for large models, the reconstructions produced by the LLM rarely reach a similar length. This suggests that the best use of AI involves the creation of small modular Alloy code, rather than large monoliths.

The difference in distributions at the left tail indicates that the LLM is biased towards generating smaller models than the ones in the corpus. This suggests that in the process of summarization and reconstruction, there is either a decrease in verbosity, or a loss of detail and complexity.

When the relation between the sizes of the original model, the reconstruction and the summary is explored in further detail, the following becomes apparent:

![](./correlation%20between%20size%20of%20original%20and%20reconstructed%20model.png)


![](./correlation%20between%20size%20of%20model%20and%20LLM-generated%20summary.png)

1) The reconstructed model shows a strong positive correlation upto models of around 1000 lines, after which the size of the reconstructed model plateaus out. This strongly suggests that the LLM tends to recreates models of a similar size as the original, provided it is not hampered by the response window.

2) There is no correlation between the length of the summary and the length of the model being summarized, possibly because the LLM uses all the available response length to explain the model. In case of simple models, the explanation could be more verbose, expanding to fill up the response window.


### Analysis of comments:

For languages which are designed to be easily readable, the best coding standards recommend self-commented code whose purpose is evident upon reading (for instance, using practices like descriptive variable names). In case the language's syntax is highly specialized or otherwise difficult to read for the layperson, a liberal policy is recommended for writing comments (since the difficulties cuased by the presence of an unnecessary comment is much less than the absence of a necessary comment).

In general, we expect the corpus to have fewer comments than would be seen in typical production Alloy code in a professional environment, since the corpus includes Alloy code written as part of assignments and small personal projects. When the commenting habits are compared between the corpus and the reconstructed code:

![](./Comparing%20number%20of%20comments%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Comparing%20total%20number%20of%20words%20in%20the%20comments%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

The key conclusions are:

1) LLMs tend to comment less when reconstructing a model from a summary, in comparison to the original models.

2) The comments written by LLMs tend to be shorter than the comments in the original model, possibly because the explanation of each element is presented in a separate section outside the code.

The commenting behaviour of LLMs could be amended via amending the prompt to include phrases such as "Explain the code in comments, not in a separate section". LLMs which can reliably do this present a significant advantage to the user, who need not keep switching between the code and the explanation when reading the reconstructed model.

### Analysis of signatures

Alloy models describe relations between atoms, whose types are described by signatures. Inheritance is applied to signatures using the `extends` keyword. For instance, `Man extends Person` and `Woman extends Person` in the earlier example show inheritance, where `Man` and `Woman` are subtypes of `Person`.

![](./Comparing%20number%20of%20signatures%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Comparing%20size%20of%20the%20signature%20bodies%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

When comparing the signatures generated by the LLM with the original corpus:

The LLM tends to create models with under 10 signatures. This suggests that a low accuracy for the reconstruction of large models, since a reduction in the number of signaures tends to correspond to a reduction in the model's complexity. Poorly designed signature schema could be simplified by merging signatures and eliminating unnecessary abstraction (for instance, `Person` can be eliminated by duplicating its code in both `Man` and `Woman`, reducing the total number of signatures by 1), but such reductions often result in an increase in the sizes of the signatures thus produced, which is not the case as seen in the comparison of sizes, which reveals that the LLM is slightly biased towards producing signatures with smaller sizes.

This suggests that creating multiple `.als` files with a small number of small signatures will result in a better model, which is in line with generally recommended coding practices.

![](./Correlation%20between%20number%20of%20signatures%20in%20the%20original%20and%20reconstructed%20models.png)

This shows that the reconstructed models tends to have a number of signatures lesser than or equal to the number of signatures in the original model, with a quick drop-off for models having more than 10 signatures, which supports the conclusions drawn from the earlier results.

Similar analyses, when performed for other elements like facts, preds, asserts and funs, do not produce enough data to draw any strong conclusions. The distributions are included in the appendix.


### Analysis of signature inheritance:

In general, inheritance can be represented via a directed acyclic graph [cite], where each node corresponds to a single signature. Signatures are categorized as follows:

1) type signatures (declared using the `extends` keyword)
2) subset signatures (declared using the `in` keyword)

Due to additional constraints imposed on type signatures in Alloy, the graph associated with the relations between them forms a forest-like structure, one with a set of rooted trees [cite]
in the top-level types.

While determining isomorphism for arbitrary graphs is a hard problem, determining isomorphism for sets of rooted trees is simple.

```
Algorithm:

function encode(root): # returns a unique string representation of the tree whose root is given
	if root is None:
		return ""
	child_codes = []
	for c in root.children:
		child_codes.append(encode(root))
	s = "0"
	child_codes.sort()
	for c in child_codes:
		s.append(c)
	s+="1"
	return s
```

The given algorithm produces a unique binary string for every rooted tree. For a forest of trees, a new tree is constructed where each top-level node in the forest is a child of a ultimate root node, to which this algorithm is then applied.

```
Algorithm:

function reconstruct(tree_code)
	p = None
	for n in tree_code:
		if n == 0:
			c = Node()
			c.parent = p
			if p:
				p.children.append(c)
			p = c
		else:
			p = p.parent
	return p
```

For brevity, a formal proof of correctness of the algorithms is omitted. The existence of a unique encoding and a reversible reconstruction function prove that the encoding is bijective. Applying this algorithm to the graphs associated with type signature inheritance relations, we used it along with a hashtable to enumerate the different inheritance relations in the corpus and identify the relative distributions.

```
Algorithm:

table = {}
for each model m:
	parse the model and identify the signatures
	construct a graph g representing the inheritance relations
	e = encode(g)
	if not table[e]:
		table[e]=0
	table[e]+=1
```

When the data is analysed:

![](./distribution%20of%20inheritance%20hierarchies%20(original).png)

![](./out/distribution%20of%20inheritance%20hierarchies%20(original).svg)

The legend shows the graph representations of the inheritance structures, after the introduction of a root node for the forest. The original corpus consists of a large number of models with no ingeritance at all (as seen in the graphs with a depth of 1), with a few more complex structures occuring often (as seen in the graphs with a depth greater than 1).

![](./distribution%20of%20inheritance%20hierarchies%20(reconstructed).png)

![](./out/distribution%20of%20inheritance%20hierarchies%20(reconstructed).svg)

In comparison, the models generated by the LLM consist mainly of simple inheritance structures, which suggests that the generated code often consists of signatures that do not inherit from other signatures. This could either be due to some inherent bias against inheritance when writing models, or due to the inheritance relations not being captured accurately in the summaries from which the models are reconstructed.




### Manual Analysis of summaries:

The analysis of summaries of models was carried out manually after certain automatic filters:

1) Length

To ensure that the models can be understood by a manual reviewer, all models with more than a 100 lines are removed from the dataset. To eliminate trivial models, models with less than 10 lines are removed.

2) Duplicate data:

To remove models which are very similar to each other, the following method was used to measure the degree of similarity between models:

```
Algorithm:
common(s1,s1):
	remove all spaces from both s1 and s2
	N = min(len(s1),len(s2))
	ct=0
	for i from 1 to N:
		if s1[i] == s2[i]:
			ct+=1
	return ct/N
```

for every pair of models (m1,m2) such that the similarity score exceeds 0.5, one of the models is removed from the dataset. This process continues until no such pairs remain.

3) Language

Since the manual reviewer is familiar only with english, all models with non-ASCII characters were removed (since Alloy syntax and the english is captured completely by the ASCII character set). This was necessary since the language of the summary generated by the LLM is influenced by the language of the comments and keywords in the model text.


4) Composition

The manual reviewer went through the remianing models and eliminated those which were part of bigger projects, where identifiers not present in the text itself were referenced. This was done since such models rely on contextual information not available to the LLM, making the LLM summaries incomplete.

After these filtration steps, a total of 50 models were chosen for manual review by the reviewer.


From the 50 models, a reviewer counts the number of elements in each model (defined as either a sig, fact, assert, pred or a fun), and the number of elements correctly described in the summary.

![](./Distribution%20of%20ratings%20from%20manual%20analysis.png)



## Limitations


### Selection bias:

Manual analysis of summaries is carried out only for models which are easy to read. This biases it towards models of around 100 lines, written using english identifiers (which is the language the authors are familiar with).

Large models are left out of the manual analysis. Since the automatic analyses strongly suggest that the performance of the LLM is dependent on the size of the model, the results of the manual analysis cannot be extended to apply to large models.

Very short (or empty) models, with no more than 2 signatures, are often captured exactly by the summary, making manual analysis shed no new light on the performance. Furthermore, such models are unlikely to be used in production, so manual analysis does not result in useful conclusions about the application of LLMs in generating models in industrial software engineering.

### Correctness of models:

Automatic analyses only describe the coding styles of the LLM and compare it to the styles of the original model. It does not say anything about the correctness of the generated models, since it does not compare the ASTs generated by the Alloy Ananlyzer to check for semantic similarity.

The conclusions drawn from automatic analysis are generally superficial, and cannot be used to make strong conclusions about the LLM's overall effectiveness at model reconstruction.

### Code analysis:

The analysis is performed via an ad-hoc parser created for the purpose of the project, and not the official Alloy Analyzer, since there is a large section of generated code which is almost syntactically correct, from which producing the official AST is impossible without manual editing to fix syntax errors (a costly process). The custom parser imposes looser conditions on syntactic correctness, which allows it to analyse LLM-generated code which is not strictly compliant with Alloy standards.

Furthermore, only static analysis is performed, since dynamic analysis requires that the code be parsed and excuted by the Analyzer. This poses a significant hindrance to drawing conclusions about the correctness of the generated models.

### Data duplication:

When assignments are uploaded to GitHub (from which the original model is scraped), the models used in the assignments tend to appear several times in the dataset. This was accounted for in manual analysis (via rejecting multiple instances of similar-looking models, for diversity) but is a significant factor in the automatic analyses. One possible mitigation strategy is to use a distance metric between strings to identify groups of models that appear to originate from the same base model, for deduplication of data.



## Future work:

A possible avenue for future work could be a comparative study between different LLMs and their abilities to generate Alloy code. This could cover both general purpose LLMs (like GPT-4, Claude, Gemini etc.) and variants of LLMS specifically trained to develop code (like codellama). As LLMs get more powerful at writing code, we would expect to see an increase in the ability to generate valid and useful Alloy code.

Given a set of valid models, a possible extension of this project is to use the ASTs generated by Alloy Analyzer for structural analysis of the generated code. One can go further and perform dynamic code analysis by running the reconstructed models using Alloy Analyzer to see how closely the outputs align with the original models.


## Acknowledgements

- scraping corpus
- deepseek company

## References

- Software Abstractions, D. Jackson
- Static Profiling of Alloy Models - Elias Eid, Nancy A. Day
https://alloytools.org/download/alloy-language-reference.pdf says 

The subset signatures and their parents
therefore form a directed acyclic graph, rooted in type signatures. The
type of a subset signature is a union of top-level types or subtypes, con-
sisting of the parents of the subset that are types, and the types of the
parents that are subsets.

he type signatures therefore form
a type hierarchy whose structure is a forest: a collection of trees rooted
in the top-level types.

- relevant papers?

## Appendix:

![](./Comparing%20number%20of%20asserts%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Correlation%20between%20number%20of%20asserts%20in%20the%20original%20and%20reconstructed%20models.png)

![](./Comparing%20number%20of%20facts%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Correlation%20between%20number%20of%20facts%20in%20the%20original%20and%20reconstructed%20models.png)

![](./Comparing%20number%20of%20funs%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Correlation%20between%20number%20of%20funs%20in%20the%20original%20and%20reconstructed%20models.png)

![](./Comparing%20number%20of%20preds%20in%20the%20corpus%20vs%20the%20reconstructed%20models.png)

![](./Correlation%20between%20number%20of%20preds%20in%20the%20original%20and%20reconstructed%20models.png)