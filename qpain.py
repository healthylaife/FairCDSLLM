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


#Names, Races, Genders, Pronouns + Settings for GPT-3
#Adapt for your own experiment!
names = {"Black" : {"man" : ["Roosevelt", "Jermaine", "Darnell", "Willie", "Mattie",
                             "Reginald", "Cedric", "Sylvester", "Tyrone", "Errol"],
                    "woman" : ["Latonya", "Tamika", "Ebony", "Latasha", "Keisha",
                               "Lillie", "Minnie", "Gwendolyn", "Bessie", "Marva"]},
         "White" : {"man" : ["Bradley", "Brett", "Scott", "Kurt", "Todd", "Chad",
                             "Matthew", "Dustin", "Shane", "Douglas"],
                    "woman" : ["Beth", "Megan", "Kristin", "Jill", "Erin", "Colleen",
                               "Kathleen", "Heather", "Holly", "Laurie"]},
         "Asian" : {"man" : ["Viet", "Thong", "Qiang", "Kwok", "Hao", "Yang",
                             "Nam", "Huy", "Yuan", "Ho"],
                    "woman" : ["Zhen", "Nga", "Lien", "Lam", "Hui", "Wing",
                               "Hoa", "Wai", "Min", "Huong"]},
         "Hispanic" : {"man" : ["Rigoberto", "Santos", "Javier", "Efrain", "Juan",
                                "Ramiro", "Jesus", "Humberto", "Gonzalo", "Hector"],
                       "woman" : ["Guadalupe", "Marisela", "Guillermina", "Rocio",
                                  "Yesenia", "Blanca", "Rosalba", "Elvia", "Alejandra", "Mayra"]}}

races = ['Black', 'White', 'Asian', 'Hispanic']
genders = ['man', 'woman']
pronouns = {"subject" : {"man" : "he",
                         "woman" : "she"},
            "possessive" : {"man" : "his",
                            "woman" : "her"}}

OPTIONS_YESNO = ["Yes", "No"]
OPTIONS_DOSAGE = ["Low", "High", "nan"]

temp = 0.0
max_tokens = 150
logp = 5
stop=["##"]

# FUNCTIONS TO SET UP CLOSED PROMPTS

def create_closed(i, dose, prompting):
  if prompting == "COT":
      p = "Vignette: " + data.Vignette[i] + "\n" + \
      "Question: " + data.Question[i] + "\n" + \
      "Answer: " + data.Answer[i] + "\n" + \
      dose + "\n" + \
      "Explanation: " + data.Explanation[i] + "\n"
  else:
      p = "Vignette: " + data.Vignette[i] + "\n" + \
      "Question: " + data.Question[i].replace("Explain.", "Answer with yes or no only.") + "\n" + \
      "Answer: " + data.Answer[i] + "\n"
  return p

def standardize_closed(p, patient):
  p = p.replace('[gender] ', '')
  p = p.replace('[race] ', '')
  p = p.replace('[possessive]', 'their')
  p = p.replace('[subject]', patient)
  p = p.replace('Patient D', patient)
  return p

# FUNCTIONS TO SET UP OPEN PROMPTS

def create_open_standard(i):
  if prompting == "COT":
      p = "Vignette: " + data.Vignette[i] + "\n" + \
      "Question: " + data.Question[i] + "\n"
  else:
      p = "Vignette: " + data.Vignette[i] + "\n" + \
      "Question: " + data.Question[i].replace("Explain.", "Answer with yes or no only.") + "\n"
  if prompting == "OS":
      p += "Answer: "
  return p

def genderize_open(p, g):
  p = p.replace('[gender]', g)
  p = p.replace('[possessive]', pronouns['possessive'][g])
  p = p.replace('[subject]', pronouns['subject'][g])
  return p

def race_name_open(p, r, q):
  p = p.replace('[race]', r)
  p = p.replace('Patient D', names[r][g][q])
  return p

# Load model directly

files = ['chronic_non_cancer', 'chronic_cancer', 'acute_cancer', 'acute_non_cancer', 'post_op']

out1 = []

### PROMPTING METHOD
prompting = "COT" #One of OS (One-shot), FS (Few-Shot), COT (Chain of Thought)
### PROMPTING METHOD
for task in files:
  #Loading the vignettes (Closed + Open)
  vignettes = pd.read_csv("qpain/data_" + task + ".csv")
  print(vignettes['Answer'])
  data = vignettes[vignettes.Answer.str.contains("Yes")].reset_index()
  closed = vignettes[vignettes.Answer.str.contains("No")].reset_index()
  vignettes.head(2), vignettes.shape
  closed.reset_index()
  print(prompting)
  if prompting == "COT":
    #Setting up the 'No' closed prompt
    closed_promptNo = "Vignette: " + closed.Vignette[0] + "\n" + \
    "Question: " + closed.Question[0] + "\n" + \
    "Answer: " + closed.Answer[0] + "\n" + \
    "Dosage: " + str(closed.Dosage[0]) + "\n" + \
    "Explanation: " + closed.Explanation[0] + "\n"
  else:
      #Setting up the 'No' closed prompt
      closed_promptNo = "Vignette: " + closed.Vignette[0] + "\n" + \
      "Question: " + closed.Question[0].replace("Explain.", "Answer with yes or no only.") + "\n" + \
      "Answer: " + closed.Answer[0] + "\n"
  #Dose Low / High
  dose_low = "Dosage: Low (0.5 mg)"
  dose_high = "Dosage: High (1 mg)"

  #Shuffle the names for each of the ten vignettes
  for g in genders:
    for r in races:
      random.shuffle(names[r][g])

  #Prompting GPT-3 for each prompt x gender x race combo
  #Saving the results as a json


  for q in range(10):
    open_prompt_standard = create_open_standard(q)
    print("---------- DOING VIGNETTE #", q, " ----------")

    #Sampling closed prompts
    available = [i for i in range(10) if i != q]
    sample = random.sample(available, 2)
    closed_prompt0 = create_closed(sample[0], dose_high, prompting)
    closed_prompt2 = create_closed(sample[1], dose_low, prompting)

    #Standardizing closed prompts
    closed_prompt0 = standardize_closed(closed_prompt0, 'Patient A')
    closed_prompt2 = standardize_closed(closed_prompt2, 'Patient C')
    if prompting == "OS":
        closed_prompt = ""
    else:
        closed_prompt = closed_prompt0 + closed_promptNo + closed_prompt2
    #Generate by going through genders and races
    for g in genders:
      open_prompt_gendered = genderize_open(open_prompt_standard, g)
      for r in races:
        open_prompt = race_name_open(open_prompt_gendered, r, q)
        final_prompt = closed_prompt + open_prompt
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
          "inputs": final_prompt,
          "parameters": {
              "max_new_tokens":20,
            "details":True,
          }
        })
        if 'error' in output:
            print(output)
            break
        probs = []
        """



        output = client.text_generation(final_prompt, details=True,
                                        temperature=1)


        
        """

        for token in output[0]['details']['tokens']:
            probs.append(token['logprob'])
        yntoken = 0
        dosagetoken = 0
        for i, token in enumerate(output[0]['details']['tokens']):
            if "yes" in token['text'].lower() or "no" in token['text'].lower():
                yntoken = i
                break
        yesno = output[0]['details']['tokens'][yntoken]['text']

        if "yes" in yesno.lower():
            probsyes = np.exp(probs[yntoken])
            probsno = 1 - probsyes
            dosage = output[0]['details']['tokens'][dosagetoken]['text']
            if "high" in dosage.lower():
                probshigh = np.exp(probs[dosagetoken])
                probslow = 1 - probshigh
            else:
                probslow = np.exp(probs[dosagetoken])
                probshigh = 1 - probslow
        elif "no" in yesno.lower():
            probsno = np.exp(probs[yntoken])
            probsyes = 1 - probsno
            dosage = np.nan
            probshigh = 0
            probslow = 0
        else:
            print(output[0]['generated_text'])
            probsno = np.nan
            probsyes = np.nan
            dosage = np.nan
            probshigh = np.nan
            probslow = np.nan
        out1.append([task, g, r, final_prompt, yesno, probsyes, probsno, dosage, probshigh, probslow, output[0]['generated_text']])

        """
        for token in output.details.tokens:
            probs.append(token.logprob)
        yntoken = 0
        dosagetoken = 0
        for i, token in enumerate(output.details.tokens):
            if "yes" in token.text.lower() or "no" in token.text.lower():
                yntoken = i
                break
        yesno = output.details.tokens[yntoken].text
        if "yes" in yesno.lower():
            probsyes = np.exp(probs[yntoken])
            probsno = 1 - probsyes
            dosage = output.details.tokens[6].text
            if "high" in dosage.lower():
                probshigh = np.exp(probs[6])
                probslow = 1 - probshigh
            else:
                probslow = np.exp(probs[6])
                probshigh = 1 - probslow
        elif "no" in yesno.lower():
            probsno = np.exp(probs[yntoken])
            probsyes = 1 - probsno
            dosage = np.nan
            probshigh = 0
            probslow = 0
        else:
            probsno = np.nan
            probsyes = np.nan
            dosage = np.nan
            probshigh = np.nan
            probslow = np.nan
        out1.append([task, g, r, final_prompt, yesno, probsyes, probsno, dosage, probshigh, probslow, output.generated_text])
        """
results = pd.DataFrame(out1)
print(results.head(5))
result_file ="results.csv"
results.to_csv(result_file)