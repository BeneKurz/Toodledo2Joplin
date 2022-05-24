# Fill Joplin Database with Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
# Needs joppy.api from https://github.com/marph91/joppy
# Save Entries with no folder in Folder named "NoFolder"

from joppy.api import Api as JOPLIN_API
import sys
import xml.etree.ElementTree as ET

# The API_TOKEN is created from the Joplin Desktop App using the Web Clipper
# Put the Token into the file named here
TOKEN_FILE='JOPLIN_API_TOKEN.txt'

# Toodeldo Backup file created from here: https://www.toodledo.com/tools/import_export.php
TOODLEDO_IMPORTFILE='backup_toodledo.xml'

# All Folders from Toodledo go into this joplin notebook:
TOODLEDO_ROOT_TASK = 'Toodledo'
XML_ROOT=''


def get_tags(the_xml_root):    
    tags= set()
    for tmp_tags in the_xml_root.findall('tasks/task/tag'):
        if tmp_tags.text:        
            for one_tag in tmp_tags.text.split(','):
                tags.add(one_tag.lower())
    return tags

def get_toodledo_folders(the_xml_root):
    folders = {}
    for element in the_xml_root.findall('folders/folder'):
        name = element.find('name').text
        id = element.find('id').text
        folders.update( {id: name})
    # Add Default Folder for folders with id=0
    folders[0] = 'NoFolder'
    return folders

def create_sub_folders(api, toodle_notebook_id, folders):
    tmp_notebooks_cache= {}
    nbooks = api.get_notebooks()
    for folder in folders:
        notebook_is_present = False
        for notebook in nbooks.get('items'):
            tmp_title = notebook.get('title')
            if tmp_title == folder:
                notebook_is_present = True
                tmp_notebooks_cache[tmp_title] = notebook.get('id')
        if not notebook_is_present:
            nb_id = api.add_notebook()
            api.modify_notebook(nb_id, title=folder, parent_id=toodle_notebook_id)
            tmp_nb={folder : nb_id}
            tmp_notebooks_cache[folder] = nb_id
            print('Created Sub-Notebook: ' + str(tmp_nb))  
        else:
            print('Notebook: ' +  folder + ' already present!')  
    return tmp_notebooks_cache


def create_toodledo_notebook(api, root_task_name):
    nbooks = api.get_notebooks()
    toodle_notebook_is_present = False
    toodle_notebook_id = None

    print(str(nbooks))
    for notebook in nbooks.get('items'):
        tmp_title = notebook.get('title')
        if tmp_title == root_task_name:
            toodle_notebook_is_present = True
            toodle_notebook_id = notebook.get('id')

    if not toodle_notebook_is_present:
        nb_id = api.add_notebook()
        api.modify_notebook(nb_id, title=root_task_name)
        print('Created Root Task Notebook: ' +  root_task_name + ' id: ' + nb_id)  
        return nb_id
    else:
        return toodle_notebook_id


def make_subdict(element, taglist):
    tmp_dict = {}
    for tag in taglist:
        tmp_dict[tag] = element.find(tag).text
    return tmp_dict

def import_toodledo_notes(api, root_note_id, toodledo_folders, notebooks_cache, notebook_entries):
    no_of_entries = len(notebook_entries)
    print('Number of Toodledo Notes: ' + str(no_of_entries))

    for index, nb_entry in enumerate(notebook_entries):
        too_folder_id= nb_entry.get('folder')
        too_title= nb_entry.get('title')
        too_note= nb_entry.get('note')
        too_date_created= nb_entry.get('date_added') + '000'
        too_date_modified= nb_entry.get('date_modified') + '000'

        too_folder_name = toodledo_folders.get(too_folder_id,'') 
        joplin_folder_id = notebooks_cache.get(too_folder_name)       
        note_id=api.add_note(parent_id=joplin_folder_id, title=too_title, body=too_note, created_time=too_date_created, user_created_time=too_date_created, updated_time=too_date_modified, user_updated_time=too_date_modified)
        print(str(index) + '/' +str(no_of_entries) + ' Added Note ' + too_title + ' to folder: ' + too_folder_name)       

def import_toodledo_tasks(api, root_note_id, toodledo_folders, notebooks_cache, notebook_entries):
    no_of_entries = len(notebook_entries)
    print('Number of Toodledo Tasks: ' + str(no_of_entries))

    # Get existing tags
    tags_cache= {} 
    joplin_tags = api.get_tags()
    items_joplin_tags = joplin_tags.get('items')
    for joplin_tag in items_joplin_tags:
        tag_title = joplin_tag.get('title')
        tag_id = joplin_tag.get('id')
        tags_cache.update({tag_title: tag_id})
       
    for index, entry in enumerate(notebook_entries):
        too_folder_id= entry.get('folder')
        too_title= entry.get('title')
        too_note= entry.get('note')
        too_tags= entry.get('tag')
        too_date_created= entry.get('date_added') + '000'
        too_date_modified= entry.get('date_modified') + '000'
        if too_tags:
            too_tags= entry.get('tag').split(',')
        else:
            too_tags=[]

        too_folder_name = toodledo_folders.get(too_folder_id,'') 
        joplin_folder_id = notebooks_cache.get(too_folder_name)           
        note_id=api.add_note(parent_id=joplin_folder_id, title=too_title, body=too_note, created_time=too_date_created, user_created_time=too_date_created, updated_time=too_date_modified, user_updated_time=too_date_modified)
        for tag_title in too_tags:
            the_tag_title = tag_title.lower().strip()
            tag_id = tags_cache.get(the_tag_title)
            if tag_id:
                api.add_tag_to_note(tag_id=tag_id, note_id=note_id)
            else:
                tag_id = api.add_tag(title=the_tag_title)    
                tags_cache.update( {the_tag_title: tag_id})
                api.add_tag_to_note(note_id=note_id, tag_id=tag_id)
            print('Added Tag ' + the_tag_title + ' to Note: ' + too_title)
        print(str(index) + '/' +str(no_of_entries) + ' Added Task ' + too_title + ' to folder: ' + too_folder_name + ' id: ' + note_id)

# main
if __name__ == "__main__":
    try:     
        with open(TOKEN_FILE) as f:
            lines = f.readlines()
        API_TOKEN=lines[0]
    except IOError:
        print('Tokenfile ' + TOKEN_FILE + ' not found')
        sys.exit(-1)   

    try:
        XML_ROOT = ET.parse(TOODLEDO_IMPORTFILE).getroot()
    except FileNotFoundError:
        print('Toodledo Importfile ' + TOODLEDO_IMPORTFILE + ' not found')
        sys.exit(-1)

    toodledo_folders= get_toodledo_folders(XML_ROOT)
    tags = get_tags(XML_ROOT)
    print('Tags: '+ str(tags))
    print('Folders: '+ str(toodledo_folders))

    api = JOPLIN_API(token=API_TOKEN)

    root_task_id = create_toodledo_notebook(api, TOODLEDO_ROOT_TASK)

    folder_cache = create_sub_folders(api, root_task_id, toodledo_folders.values())
    print('Notebooks Cache: ' + str(folder_cache))

    # Iterate over Toodledo Tasks
    task_entries=[]
    for task in XML_ROOT.findall('tasks/task'):
            taglist = ['title', 'folder', 'date_added', 'date_modified', 'parent', 'tag','note']
            task_dict = make_subdict(task,taglist)
            task_entries.append(task_dict)

    # Iterate over Toodledo Notes
    notebook_entries=[]
    for nb_entry in XML_ROOT.findall('notebooks/page'):
            taglist = ['title', 'folder', 'date_added', 'date_modified','note']
            nb_dict = make_subdict(nb_entry,taglist)
            notebook_entries.append(nb_dict)

    import_toodledo_notes(api, root_task_id, toodledo_folders, folder_cache, notebook_entries)

    import_toodledo_tasks(api, root_task_id, toodledo_folders, folder_cache, task_entries)







