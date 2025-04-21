import os
import sys
import json
import re
import matplotlib.pyplot as plt


def extract_code(text):
	m = re.search(r"```(.*)```",text,re.DOTALL)
	if m:
		return m.group(1)
	return None

def extract_thoughts(text):
	m = re.search(r"<think>([^<]*)</think>",text,re.DOTALL)

print(extract_code("```\n\n\naaabbbcc```"))
