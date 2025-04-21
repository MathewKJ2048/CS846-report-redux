# CS846 project report - Applying LLMs to Alloy models

## Abstract

## Background

### Declarative modelling and Alloy

- what is declarative modelling  and UML
- explanation about alloy
- what is predicate, sig, example code etc.

### LLMs and deepseek

- what is llm
- what is special about deepseek


## Methodology

- scraping (github, explanation about the scraping thing)
- generation from LLM (with prompts, and the use of the prompt for attention), (.stream with timestamps, process stability)
- model generation, along with success rate, use of quotes to identifyu the code

two images here

## Results

### Analysis of the corpus

This section deals with a general summary of the entire corpus

- running the analysis with the analysis repository


### Analysis of summaries

This section deals with the subset of models which summaries were created for

- length of summary vs length of model
- percentage of thinking vs code vs text

manual analysis of 100 models for correctness:
- number of predicates and signatures explained correctly


### Analysis of reconstructed models

This section deals with the subset of models which summaries were created for, from which models were recreated

## Limitations

- selection bias - manual analysis carrid out for english models only
- model structure does not shed useful light on correctness
- ground truth model is not the ideal form, deviation by AI could mean mistake or a better form of the same model

## Future work:

- running with other AIs and comparative study
- running the model to see if the execution results match

## Acknowledgements

- scraping corpus
- analysis corpus
- deepseek company

## References

- Elias
- relevant papers?