# Fill Joplin Database with Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
# Needs joppy.api from https://github.com/marph91/joppy


from joppy.api import Api
import argparse
import os, sys
import xml.etree.ElementTree as ET

# The API_TOKEN is created from the Joplin Desktop App using the Web Clipper
# Put the Token into the file named here
TOKEN_FILE='JOPLIN_API_TOKEN.txt'

# Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
TOODLEDO_IMPORTFILE='backup_toodledo.xml'

# All Folders from Toodledo are put into this notebook:
TOODLEDO_ROOT_NOTEBOOK = 'Toodledo'

try:     
    with open(TOKEN_FILE) as f:
        lines = f.readlines()
    API_TOKEN=lines[0]
except IOError:
    print('Tokenfile ' + TOKEN_FILE + ' not found')
    sys.exit(-1)   

try:
    root = ET.parse(TOODLEDO_IMPORTFILE).getroot()
except FileNotFoundError:
    print('Toodledo Importfile ' + TOODLEDO_IMPORTFILE + ' not found')
    sys.exit(-1)

def get_tags():    
    tags= set()
    #for tmp_tags in root.findall('item/tag'):
    for tmp_tags in root.findall('tasks/task/tag'):
        #value = type_tag.get('foobar')
        if tmp_tags.text:        
            for one_tag in tmp_tags.text.split(','):
                tags.add(one_tag.lower())
    return tags

def get_folders():
    folders = set()        
    for tmp_folder in root.findall('folders/folder/name'):
        if tmp_folder.text:
            folders.add(tmp_folder.text)
    return folders


# Das geht nicht so, Tags können nur einer Notiz zugeordnet werden
def create_joplin_tags(api, toodledo_tags):
    joplin_tags_cache = []
    actual_joplin_tags_dict_array = api.get_all_tags()
    for actual_joplin_tag in actual_joplin_tags_dict_array:
        tmp_local_joplin_tags= {}
        #tmp_local_joplin_tags['id'] = actual_joplin_tag.get('id') 
        #tmp_local_joplin_tags['title'] = actual_joplin_tag.get('title') 
        tmp_local_joplin_tags[actual_joplin_tag.get('id')] = actual_joplin_tag.get('title') 
        joplin_tags_cache.append(tmp_local_joplin_tags)
        

    print(str(joplin_tags_cache))
    for toodledo_tag in toodledo_tags:
        found_tag = None
        for index in range(len(joplin_tags_cache)):
            for key in joplin_tags_cache[index]:
                val = joplin_tags_cache[index][key]
                if toodledo_tag == joplin_tags_cache[index][key]:
                    found_tag = toodledo_tag
        if found_tag:
            print('found: ' + found_tag)
        else:
            tmp_tag_id = api.add_tag()
            api.modify_tag(tmp_tag_id, title=toodledo_tag)
            print

    # for toodledo_tag in toodledo_tags:
    #     for joplin_tags_cache_item in joplin_tags_cache:
    #         if toodledo_tag == 

        # present_tags = [li['title'] for li in joplin_tags_cache]
        # if toodledo_tag in 

    print(str(joplin_tags_cache)) 
    #present_tags = [li['title'] for li in actual_joplin_tags_dict]
    #print(str(present_tags))
    # for tag_to_insert in tags_set:
    #     for joplin_tag in joplin_tags:
    #         print(str(joplin_tag.get('title')))

    return local_joplin_tags
        

def create_sub_notebooks(api, toodle_notebook_id, folders):
    tmp_notebooks_cache= []
    nbooks = api.get_notebooks()
    for folder in folders:
        notebook_is_present = False
        for notebook in nbooks.get('items'):
            tmp_title = notebook.get('title')
            if tmp_title == folder:
                notebook_is_present = True
                tmp_nb={'title' : tmp_title, 'id' : notebook.get('id')}
                tmp_notebooks_cache.append(tmp_nb)

                
        if not notebook_is_present:
            nb_id = api.add_notebook()
            api.modify_notebook(nb_id, title=folder, parent_id=toodle_notebook_id)
            tmp_nb={'title' : folder, 'id' : nb_id}
            tmp_notebooks_cache.append(tmp_nb)
            print('Created Notebook: ' + str(tmp_nb))  
        else:
            print('Notebook: ' +  folder + ' already present!')  
    return tmp_notebooks_cache


def create_toodledo_notebook(api):
    nbooks = api.get_notebooks()
    toodle_notebook_is_present = False
    toodle_notebook_id = None

    print(str(nbooks))
    for notebook in nbooks.get('items'):
        tmp_title = notebook.get('title')
        if tmp_title == TOODLEDO_ROOT_NOTEBOOK:
            toodle_notebook_is_present = True
            toodle_notebook_id = notebook.get('id')


    if not toodle_notebook_is_present:
        nb_id = api.add_notebook()
        api.modify_notebook(nb_id, title=TOODLEDO_ROOT_NOTEBOOK)
        print('Created Notebook: ' +  TOODLEDO_ROOT_NOTEBOOK + ' id: ' + nb_id)  
        return nb_id
    else:

        return toodle_notebook_id
        sys.exit(-1) 



folders= get_folders()
tags = get_tags()
print('Tags: '+ str(tags))
print('Folders: '+ str(folders))

api = Api(token=API_TOKEN)


nb_id = create_toodledo_notebook(api)
print('Notebook: ' +  TOODLEDO_ROOT_NOTEBOOK + ' id: ' + nb_id)  

notebooks_cache = create_sub_notebooks(api, nb_id, folders)
print('Notebooks Cache: ' + str(notebooks_cache))



#create_joplin_tags(api,tags)





