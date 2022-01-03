#!/usr/local/bin/python

# TODO: this is a dumb script, use grep instead :P

import os

path = "."
print("checking serverless.yml files for Alexa Skill Id's")
for root, directories, files in os.walk(path, topdown=False):
    for name in files:
        if 'serverless.yml' in name:
            file_path = os.path.join(root, name)
            with open(file_path,'r') as file_obj:
                for line in file_obj.readlines():
                    if 'alexaSkill' in line and 'amzn1.ask.skill.' in line:
                        print("Don't commit the Alexa Skill Id in the serverless.yml file.")
                        print(f"Line: \r\n    {line}")
                        print(file_path)
                        exit(1)
print("No Alexa Skill Id's found in serverless.yml files")
exit(0)
