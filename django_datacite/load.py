import json
from ..gfz_dataservices.models import Keyword


def parse(obj):
    map = Keyword.mapping
    fields = [f.name for f in Keyword._meta.get_fields()]
    return {f: obj.get(map[f], None) for f in fields if f in map.keys()}

def add_children(parent, children):
    """parent is a Keyword object, children is a list of dictionaries containing children """
    if children:
        parent = Keyword.objects.get(pk=parent.pk)

    for child in children:
        child_node = parent.add_child(**parse(child))
        add_children(child_node, child.get('children', []))


def load():

    with open('gfz_dataservices/data/keywords.json', encoding='utf-8') as f:
        thesaurus = json.load(f)
        
    for obj in thesaurus['children']:
        root = Keyword.add_root(**parse(obj))       
        add_children(root, obj.get('children', []))