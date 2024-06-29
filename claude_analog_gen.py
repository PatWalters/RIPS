#!/usr/bin/env python

import anthropic
import json
import pandas as pd
from tqdm.auto import tqdm
import unicodedata

#Claude sometimes puts odd control characters in the cause problems with json.loads
def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def generate_analogs(input_smiles):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system="You are a world-class medicinal chemist.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate SMILES strings for 100 analogs of the molecule represented by the SMILES {input_smiles}, you can modify both the core and the substituents. Return only the SMILES as a python list. Dont put in line breaks. Don't put the prompt into the reply"
                    }
                ]
            }
        ]
    )
    res = message.content
    txt = res[0].text
    # hacks to clean up bad strings returned by Claude
    txt = remove_control_characters(txt)
    txt = txt.encode('unicode_escape').decode()
    # end hacks
    try:
        smi_list = json.loads(txt)
    except:
        smi_list = []
    return smi_list

df = pd.read_csv("fragment_lead_pairs_no_boron.csv")
out_list = []
for idx,smi in enumerate(tqdm(df.Fragment.values)):
    for res in generate_analogs(smi):
        out_list.append([idx,res,smi])
out_df = pd.DataFrame(out_list,columns=["Idx","SMILES","Input_SMILES"])
out_df.to_csv("claude_samples.csv",index=False)
