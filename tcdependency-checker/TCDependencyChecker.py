'''
This tool script is created for analyze the addon files which is contain 
in the truclient extension folder.

Parse the json file to dot language and compile with dot
graphviz.com

Addin will be draw with yellow, File will be draw with blue and Dir will be draw with red
'''

import json
import os 
import pickle
import sys
import code 
import anytree
import networkx
from glob import glob
from pprint import pprint as pp 


isPy2 = sys.version_info[0] == 2
isPy3 = sys.version_info[0] == 3

if isPy3:
    string_types = str
else:
    string_types = basestring
   
extension_path = r"F:\tclite\Extension"
addin_graph = None 
addin_trees = None 
ADDIN, DIR, FILE, JSON = 'AddIn', 'Dir', 'File', 'JSON'
ROOT = '_root'

def get_path_info(basePathes, extension_path):
    '''
    compose a path information object contain such as baseUrlRRE, baseUrlExt, etc. to a addin path dict 

    '''
    basePathes = list(basePathes)
    subfolders = []

    for p in basePathes:
        p = p.replace('baseUrl', '')
        if p and os.path.isdir(os.path.join(os.path.join(extension_path, p), "content")):
            p = os.path.join(p, "content")
        subfolders.append(p)

    return dict(zip(basePathes, [os.path.join(extension_path, s) for s in subfolders]))

def find_all_json(extension_path):
    '''
    return a list of finded addin file pathes 
    '''
    fjsons = []
    addin_path = os.path.join(extension_path, "AddIns")
    for root, dirs, files in os.walk(addin_path):
        for f in files:
            if f.endswith('.json'):
                fjsons.append(os.path.join(root, f))

    return fjsons

def load_jsons(fjsons):
    jsons = []
    for j in fjsons:
        jsons.append(json.load(open(j, 'r')))

    return jsons 

def find_all_basePathes(jsons):
    basePathes = set()
    for j in jsons:
        for key_type, items in j.items():
            if key_type == 'loadOrder':
                for item in items:
                    basePath = item.get('basePath')
                    if basePath:
                        basePathes.add(basePath)
    return basePathes

def init(path):
    global extension_path
    global addin_trees
    global addin_graph
    extension_path = path

    print('loading addin json files')
    fjsons    = find_all_json(extension_path)
    jsons     = load_jsons(fjsons)
    addin_map = {}
    for i in range(len(fjsons)):
        addin_map.setdefault(os.path.split(fjsons[i])[1][:-5], jsons[i])

    path_info   = get_path_info(find_all_basePathes(jsons), extension_path)
    addin_graph = build_addin_dependency_graph(addin_map)
    addin_trees = {addin_name:add_file_leaves(build_addin_tree(addin_name, json), path_info) for addin_name, json in addin_map.items()}
    print('init compelete')

def check(name, node_type=None):
    if not name:
        print('name is required')
        return

    name = name.strip()
    if not node_type:
        if name.endswith('.json'):
            node_type = 'addin'
            name = name[:-5]
        elif name.endswith('.js'):
            node_type = 'file'
            name = name[:-3]
        else:
            node_type = 'dir'

    addin_node_trees = {addin_name:get_node_dependency_trees(name, node_type, tree) for addin_name, tree in addin_trees.items()}
    finded_trees     = [concat_dependency_trees(node_tree, get_addin_dependency_tree(addin_name, addin_graph)) 
                            for addin_name, node_trees in addin_node_trees.items() 
                            for node_tree in node_trees]
    for tree in finded_trees:
        render_tree(tree)
    
def build_addin_dependency_graph(addin_map):
    '''
    build an addin dependency graphic 
    '''
    g = networkx.DiGraph()
    for addin_name, json in addin_map.items():
        if json.get('loadOrder'):
            g.add_node(addin_name)
            for item in json['loadOrder']:
                if item['type'] == ADDIN:
                    g.add_edge(addin_name, item['name'])
        else:
            print("warning: the addin %s doesn't contain any loadOrder information" % addin_name)

    return g

def get_addin_dependency_tree(addin, addin_graph):
    '''
    find the addin dependencies, which means the other addins are included in the addin,
    the result will be a dependency tree, the root is the aim addin
    '''
    root = anytree.Node(addin, type=ADDIN)
    cur_node = root
    predecessors = []
    while True:
        for pre in addin_graph.predecessors(addin):
            predecessors.append(pre)
        if predecessors:
            addin = predecessors.pop()
            cur_node = anytree.Node(addin, parent=cur_node, type=ADDIN)
        else:
            break
    return root

def get_node_dependency_trees(name, node_type, addin_tree):
    '''
    search for the aim item by name in the addin_tree, and build a new dependency tree.
    if the name could not be found in the addin_tree than return None
    '''
    nodes = []
    trees = []
    name = name.lower()
    node_type = node_type.lower()
    for node in anytree.PreOrderIter(addin_tree):
        if node.name.lower() == name and node.type.lower() == node_type:
            nodes.append(node)

    for node in nodes:
        root = anytree.Node(node.name, type=node.type, data=node.data)
        cur_node = root
        while node.parent:
            node = node.parent
            if node.type != JSON: # don't inlucde the addin json node itself
                cur_node = anytree.Node(node.name, type=node.type, data=node.data, parent=cur_node)
        trees.append(root)
    return trees

def concat_dependency_trees(node_dep_tree, addin_dep_tree):
    '''
    concat two dependency trees into a single one base on the addin name, if the addin name
    is not match then will return None
    '''
    for tail in anytree.PostOrderIter(node_dep_tree):
        addin_dep_tree.parent = tail 
        return node_dep_tree

def render_tree(tree):
    for pre, fill, node in anytree.RenderTree(tree):
        if node.type == FILE:
            print("%s%s.js" % (pre, node.name))
        elif node.type == ADDIN:
            print("%s%s.json" % (pre, node.name))
        else:
            print("%s%s" % (pre, node.name))
    print('\n')

def build_addin_tree(addin_name, json):
    '''
    convert the json to a tree structure, each child node's type should be dir/file/addin. the 
    root node type is json which map to each addin file
    '''
    addin_root = anytree.Node(addin_name, type=JSON, data=json) 
    for key, items in json.items():
        if key == 'loadOrder':
            addin_root.items = items
            for data in items:
                item_node = anytree.Node(data['name'], parent=addin_root, type=data['type'], data=data)
    return addin_root
    
def add_file_leaves(addin_tree, path_info):
    '''
    iterate from the root of a tree and add all the dependent files information
    for each node which type is not a file
    '''
    parent_child_pairs = []
    for node in anytree.PreOrderIter(addin_tree):
        if node.type == DIR:
            base_path = path_info[node.data['basePath']]
            descriptor_name = '%s.json' % node.data.get('descriptorName', node.name)
            descriptor_dir  = os.path.join(base_path, node.name)
            descriptor_path = os.path.join(descriptor_dir, descriptor_name)
            if os.path.isfile(descriptor_path):
                for module in json.load(open(descriptor_path, 'r'))["modules"]:
                    module_path = os.path.join(base_path, '%s.js' % module)
                    child = anytree.Node(module, type=FILE, data={"type":FILE, "name":module, "basePath":base_path})
                    parent_child_pairs.append((node, child))
            else:
                print('Warning: addin file %s could not be founded in path %s! Try to load all the JS files' % (descriptor_name, descriptor_dir))
                for file in os.listdir(descriptor_dir):
                    if file.endswith('.js'):
                        module = file[:-3]
                        child = anytree.Node(module, type=FILE, data={"type":FILE, "name":module, "basePath":base_path})
                        parent_child_pairs.append((node, child))

        elif node.type == FILE:
            node.data['name'] = node.data['name'].split('/')[-1]
    for pair in parent_child_pairs:
        parent, child = pair
        child.parent = parent
    return addin_tree
 
if __name__ == '__main__':
    banner = """TruClient addins look up tool version 1.0.

    Introduction:
    This tool is design for find a dependencies between a JavaScript file, directory or AddIn base 
    from the <TC dir>/extension/AddIns. For example when you changed a JavaScript file you want to 
    check what's the enflunce to the existing AddIns in other product.
    
    Use steps:
    1. init the tool with truclient extension path
    >>> init(<the path of the extension folder>)

    2. use the function check to display a dependency information
    >>> check(<name>, [type])

    supported types: file, dir, addin 

    Examples:
    >>> init('f:/tclite/extension')
    >>> check('ident.js')
    >>> check('ident', 'file')
"""
    code.interact(banner, local={'init':init, 'check':check})



    