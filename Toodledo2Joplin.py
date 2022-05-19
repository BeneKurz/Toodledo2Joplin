# Fill Joplin Database with Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
# Needs joppy.api from https://github.com/marph91/joppy


from joppy.api import Api as JOPLIN_API
import argparse
import os, sys
import xml.etree.ElementTree as ET
import xmltodict
from pprint import pprint

# The API_TOKEN is created from the Joplin Desktop App using the Web Clipper
# Put the Token into the file named here
TOKEN_FILE='JOPLIN_API_TOKEN.txt'

# Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
TOODLEDO_IMPORTFILE='backup_toodledo.xml'

# All Folders from Toodledo are put into this notebook:
TOODLEDO_ROOT_NOTEBOOK = 'Toodledo'

XML_ROOT=''

try:     
    with open(TOKEN_FILE) as f:
        lines = f.readlines()
    API_TOKEN=lines[0]
except IOError:
    print('Tokenfile ' + TOKEN_FILE + ' not found')
    sys.exit(-1)   


def get_tags(the_xml_root):    
    tags= set()
    #for tmp_tags in root.findall('item/tag'):
    for tmp_tags in the_xml_root.findall('tasks/task/tag'):
        #value = type_tag.get('foobar')
        if tmp_tags.text:        
            for one_tag in tmp_tags.text.split(','):
                tags.add(one_tag.lower())
    return tags

def get_folders(the_xml_root):
    folders = set()        
    for tmp_folder in the_xml_root.findall('folders/folder/name'):
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

def make_subdict(element, taglist):
    tmp_dict = {}
    for tag in taglist:
        tmp_dict[tag] = element.find(tag).text
    return tmp_dict

def get_todledo_entries(api, xml_root):
    # Siehe Finding interesting elements: https://docs.python.org/3/library/xml.etree.elementtree.html
    for task in xml_root.findall('tasks/task'):
        taglist = ['title', 'folder', 'date_added', 'date_modified', 'parent', 'tag','note']
        subdict = make_subdict(task,taglist)
        print(str(subdict))

        
        bene = 1234


    # entries = []        
    # for task in the_xml_root.findall('tasks/task'):
    #     x=(task.tag)
    #     z=list(x)
    #     for i in z:
    #         print(x[i])

        # bene = xmltodict.parse(task)
        # pprint(bene)
        # title = task.findall('title/attrib')
        # print(str(title))

        # task_title = task.get('title')
        # print(str(task_title))

    

# main
try:
    XML_ROOT = ET.parse(TOODLEDO_IMPORTFILE).getroot()
except FileNotFoundError:
    print('Toodledo Importfile ' + TOODLEDO_IMPORTFILE + ' not found')
    sys.exit(-1)

folders= get_folders(XML_ROOT)
tags = get_tags(XML_ROOT)
print('Tags: '+ str(tags))
print('Folders: '+ str(folders))

api = JOPLIN_API(token=API_TOKEN)

#bene = xmltodict.parse(XML_ROOT)


nb_id = create_toodledo_notebook(api)
print('Notebook: ' +  TOODLEDO_ROOT_NOTEBOOK + ' id: ' + nb_id)  

notebooks_cache = create_sub_notebooks(api, nb_id, folders)
print('Notebooks Cache: ' + str(notebooks_cache))

# Iterate over Tasks and create them as Entries
task_entries=[]
for task in XML_ROOT.findall('tasks/task'):
        taglist = ['title', 'folder', 'date_added', 'date_modified', 'parent', 'tag','note']
        task_dict = make_subdict(task,taglist)
        task_entries.append(task_dict)
        print(str(task_dict))

notebook_entries=[]
for nb_entry in XML_ROOT.findall('notebooks/page'):
        taglist = ['title', 'folder', 'date_added', 'date_modified','note']
        nb_dict = make_subdict(nb_entry,taglist)
        notebook_entries.append(nb_dict)
        print(str(nb_dict))


print('Number of Tasks: ' + str(len(task_entries)))
print('Number of notebook-Entries: ' + str(len(notebook_entries)))

# get_todledo_entries(api, XML_ROOT)



#create_joplin_tags(api,tags)





