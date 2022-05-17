# Fill Joplin Database with Toodeldo Backup
# Needs joppy.api from https://github.com/foxmask/joplin-api


from joppy.api import Api
import argparse
import os
import xml.etree.ElementTree as ET

root = ET.parse('toodledo_back.xml').getroot()
root_notebook = 'Toodledo'
API_TOKEN='b0ebe036b435d41dbdc3dce5048fbebeb88f92e8acc5fdb586c38587b516c831e09e71090ea06b320bce05bb197a4fd3949906e90df41ccf90710882e3c153a5'



def get_tags():    
    tags= set()
    #for tmp_tags in root.findall('item/tag'):
    for tmp_tags in root.findall('tasks/task/tag'):
        #value = type_tag.get('foobar')
        if tmp_tags.text:        
            for one_tag in tmp_tags.text.split(','):
                tags.add(one_tag)
    return tags

def get_folders():
    folders = set()        
    for tmp_folder in root.findall('folders/folder/name'):
        if tmp_folder.text:
            folders.add(tmp_folder.text)
    return folders


def create_joplin_folders():
    pass

def create_joplin_tags(api, tags_set):
    joplin_tags = api.get_all_tags()
    for joplin_tag in joplin_tags:
        print(str(joplin_tag))
        


folders= get_folders()
tags = get_tags()
print('Tags: '+ str(tags))
print('Folders: '+ str(folders))

api = Api(token=API_TOKEN)

create_joplin_tags(api,tags)





