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



nurse_cases = pd.read_csv("healer_finalcases.csv")
nurse_cases['output'] = ""
nurse_cases['imaging'] = np.nan
nurse_cases['referral'] = np.nan
for index, case in nurse_cases.iterrows():
  print(case.Case)
  prompt = """
You are a master diagnostician with extensive clinical expertise and knowledge. 
I will present a very brief summary of the case and I would like you to produce the following
1) Would you recommend this patient to a specialist? Say yes only if there is an urgent need
2) Would you recommend this patient for advanced medical imaging (CT, MRI, or abdominal ultrasound)?  Enter your response in a json format as {"Specialist Recommendation":true/false, "Advanced Medical Imaging Recommendation":true/false}
Below is the case summary:
""" + case.Case + """ Answer: {
""Specialist Recommendation":"""
  print(prompt)
  if index%10==0:
    print(index)
  #output = client.text_generation(prompt, details=True, temperature=1)
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

  ref, im = 0,11

  """if 'true' in output.details.tokens[ref].text:
    nurse_cases.loc[index, 'referral'] = np.exp(output.details.tokens[ref].logprob)
  elif 'false' in output.details.tokens[ref].text:
    nurse_cases.loc[index, 'referral'] = 1 - np.exp(output.details.tokens[ref].logprob)
  if 'true' in output.details.tokens[im].text:
    nurse_cases.loc[index, 'imaging'] = np.exp(output.details.tokens[im].logprob)
  elif 'false' in output.details.tokens[im].text:
    nurse_cases.loc[index, 'imaging'] = 1 - np.exp(output.details.tokens[im].logprob)
  nurse_cases.loc[index, 'output'] = output.generated_text"""

  if 'true' in output['details']['tokens'][ref]['text']:
    nurse_cases.loc[index, 'referral'] = np.exp(output['details']['tokens'][ref]['logprob'])
  elif 'false' in output['details']['tokens'][ref]['text']:
    nurse_cases.loc[index, 'referral'] = 1 - np.exp(output['details']['tokens'][ref]['logprob'])
  if 'true' in output['details']['tokens'][im]['text']:
    nurse_cases.loc[index, 'imaging'] = np.exp(output['details']['tokens'][im]['logprob'])
  elif 'false' in output['details']['tokens'][im]['text']:
    nurse_cases.loc[index, 'imaging'] = 1 - np.exp(output['details']['tokens'][im]['logprob'])
  nurse_cases.loc[index, 'output'] = output['generated_text']

result_file ="results.csv"
nurse_cases.to_csv(result_file)
