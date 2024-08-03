from typing import List
from requests import post, get
import json
from time import strftime
import os
import yaml
import pprint
from string import Template

pwd = os.getcwd()
now = strftime("%Y-%m-%d %H-%M-%S")
runpath = f"{pwd}/{now}"

def main(): 
    config = parse_config()
    setup_run(config)
    runpath = setup_env()
    os.chdir(runpath)
    ic_procedure = build_procedure(steps_ic)
    #pprint.pp(ic_procedure)
    execute_procedure(ic_procedure)
    oc_procedure = build_procedure(steps_oc,samples)
    #pprint.pp(oc_procedure)
    execute_procedure(oc_procedure)

## Setup

def parse_config() -> dict:
    with open("run_config.yaml",'r') as file:
        config = {}
        for x in yaml.safe_load_all(file): config.update(x)
    return config

def setup_env():
    if os.path.exists(runpath): raise Exception(f"Runpath already exists! I don't get paid enough for time travel shenanigans...\nLook, more than likely your clock changed. Give it a bit or delete {runpath}, ok?")
    os.mkdir(runpath)
    for step in steps_ic:
        file = f"{runpath}/{step}"
        y = open(file,"x"); y.close
    for x in samples:
        file = f"{runpath}/oc_eval_{x}"
        y = open(file,"x"); y.close
    
    return runpath

# I fucking despise accessing members of nested dictionaries in Python, so
# I'm pulling out all the things I need into global variables. Go pout
def setup_run(config):
    global llm_params; llm_params = config["llm_params"] 
    global system_tag; system_tag = llm_params["system_tag"]
    global system_prompt; system_prompt = llm_params["system_prompt"]
    global user_tag; user_tag = llm_params["user_tag"]
    global bot_tag; bot_tag = llm_params["bot_tag"]
    global history; history = llm_params["history_prefill"]
    global context_template; context_template = llm_params["context_template"]

    global kobold_params; kobold_params = config["kobold_params"]
    global url; url = config["meta"]["url"]

    global story; story = config["story_details"]
    global ratings; ratings = config["ratings"]
    global rating; rating=story["rating"]
    global rating_string; rating_string = ratings[story["rating"]]
    global tags; tags = story["tags"]
    
    global steps; steps = config["steps"]
    global steps_ic; steps_ic = steps["ic"]
    global steps_oc; steps_oc = steps["oc_eval"]

    # multi-shot eval stuff
    global focus; focus = story["focus"]
    global samples; samples = config["meta"]["eval_inputs"]

## Prompt "Engineering"
def reset_history():
    return llm_params["history_prefill"]

## builds a prompt from the existing history and a string to be the "request"
def build_prompt(history,request) -> str:
    input = f"{user_tag}{request}{bot_tag}"
    # strings that are read from run_config.yaml are templates
    prompt = Template(context_template).substitute(
        system_tag=system_tag,
        system_prompt=system_prompt,
        history=history or "", # surprised that this works. onya python
        input=input
    )
    return prompt

def build_instruction(request,infile=False) -> str:
    if not infile: story_text=""
    else:
        with open(infile) as sample:
            story_text = sample.read()
            if story_text == "": raise Exception(f"Attempt to read {infile} returned an empty string")
    instruction = Template(request).substitute(
        rating=rating,
        rating_string=rating_string,
        story_text=story_text,
        tags=tags,
        focus=focus
    )
    return instruction
    
def build_procedure(portion,infiles=[""]) -> List[str]:
    procedure = []
    proc_steps = portion.keys()
    print(f"Input files for procedure:{infiles}")
    for file in infiles:
        for i in proc_steps:
            step = portion[i].copy()
            if "outfile" not in step:
                step["outfile"] = f"oc_eval_{file}"
            if "clearHistory" not in step:
                step["clearHistory"] = False
            step["prompt"] = build_instruction(step["prompt"],file)
            procedure.append(step)
    return procedure

def execute_step(step, history):
    code = 0
    if step["clearHistory"] == True: history=reset_history()
    file = step["outfile"] 
    outfile = open(f"{runpath}/{file}","a")
    prompt = build_prompt(history,step["prompt"])
    
    print(f"##PROMPT:\n{prompt}")
    output = ""
    while code == 0:
        response = generate(kobold_params,prompt+output)
        history = history+response
        code = query_stop()
        output = output+response

    #print(f"##OUTPUT FILE:\{outfile.name}")
    print(f"##OUTPUT:\n{output}")
    outfile.write(output)
    return history

def execute_procedure(procedure):
    history = reset_history()
    for step in procedure:
        history = execute_step(step, history)

## KoboldCPP Interaction
def generate(payload, prompt) -> str:
    endpoint = f"{url}/v1/generate"
    payload["prompt"] = prompt
    request = post(endpoint,json=payload)
    response = json.loads(request.text)
    output = (response["results"][0]["text"])
    return output

## Query Stop Reason (for continuation)
def query_stop() -> str:
    request = get(f"{url}/extra/perf")
    response = json.loads(request.text)
    code = response["stop_reason"]
    return code

main()