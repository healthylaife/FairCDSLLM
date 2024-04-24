# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#SETTING UP
from argparse import ArgumentParser
import pandas as pd
import numpy as np
np.random.seed(42)
import random
random.seed(42)
from functools import partial
import json


nurse_cases = pd.read_csv("GPTBias/gpt4_bias/preprocessing/unconscious_bias_nurses_final.csv")
nurse_cases['output'] = ""
for index, case in nurse_cases.iterrows():
  prompt = """
""" + case.system + " " + case.prompt + """Enter your response in a JSON format. {Answer: """
  if index%10==0:
    print(index)

  import requests

  API_URL = "https://XXX.us-east-1.aws.endpoints.huggingface.cloud"
  headers = {
    "Accept": "application/json",
    "Authorization": "Bearer XXX",
    "Content-Type": "application/json"
  }


  def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


  output = query({
    "inputs": prompt,
    "parameters": {
      "temperature": 1,
      "details": True,
    }
  })[0]
  print(prompt)
  #output = client.text_generation(prompt, details=True, temperature=1)
  nurse_cases.loc[index, 'output'] = output.generated_text

result_file ="results/nurse/results_nurse_llama.csv"
nurse_cases.to_csv(result_file)
