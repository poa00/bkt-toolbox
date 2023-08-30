# -*- coding: utf-8 -*-

# https://fontawesome.com/v4.7.0/



import os.path
import io
import json
from collections import OrderedDict,defaultdict

import bkt
from bkt.library.powerpoint import PPTSymbolsGallery


# define the menu parts

menu_title = 'Material Icons'

symbols_common = [
    ("Material Icons", "\uE853", "account circle", "Material Icons > Wichtige"),
    ("Material Icons", "\uE897", "lock", "Material Icons > Wichtige"),
    ("Material Icons", "\uE8DC", "thumbs up", "Material Icons > Wichtige"),
    ("Material Icons", "\uE8DB", "thumbs down", "Material Icons > Wichtige"),
    ("Material Icons", "\uE0B0", "call", "Material Icons > Wichtige"),
    ("Material Icons", "\uE0B7", "chat", "Material Icons > Wichtige"),
    ("Material Icons", "\uE0BE", "email", "Material Icons > Wichtige"),
    ("Material Icons", "\uE2BD", "cloud", "Material Icons > Wichtige"),
    ("Material Icons", "\uE7EF", "group", "Material Icons > Wichtige"),
    ("Material Icons", "\uE7FD", "person", "Material Icons > Wichtige"),
    ("Material Icons", "\uE55F", "place", "Material Icons > Wichtige"),
    ("Material Icons", "\uE80B", "public", "Material Icons > Wichtige"),
]

menu_settings = [
    # menu label,          list of symbols,       icons per row
    ('Wichtige',          symbols_common,           6  ),
]

def get_content_categories():
    # Automatically generate categories from json file from https://gist.github.com/AmirOfir/daee915574b1ba0d877da90777dc2181
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "materialicons.json")
    with io.open(file, 'r', encoding='utf-8') as json_file:
        chars = json.load(json_file, object_pairs_hook=OrderedDict)

    # categories = OrderedDict()
    categories = defaultdict(list)
    for char in chars['categories']:
        for ico in char['icons']:
            t=(
                "Material Icons",
                chr(int(ico['codepoint'], 16)),
                ico['name'],
                "Material Icons > {}\n{}".format(char['name'].capitalize(), ico.get('keywords', [""])[0])
            )
            categories[char['name'].capitalize()].append(t)
    
    return bkt.ribbon.Menu(
                xmlns="http://schemas.microsoft.com/office/2009/07/customui",
                id=None,
                children=[
                    PPTSymbolsGallery(label="{} ({})".format(cat, len(categories[cat])), symbols=categories[cat], columns=16)
                    for cat in sorted(categories.keys())
                ]
            )

def update_search_index(search_engine):
    search_writer = search_engine.writer()

    # Automatically generate categories from json file from https://gist.github.com/AmirOfir/daee915574b1ba0d877da90777dc2181
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "materialicons.json")
    with io.open(file, 'r', encoding='utf-8') as json_file:
        chars = json.load(json_file, object_pairs_hook=OrderedDict)
        
        for char in chars['categories']:
            for ico in char['icons']:
                search_writer.add_document(
                    module="materialicons",
                    fontlabel="Material Icons",
                    fontname="Material Icons",
                    unicode=chr(int(ico['codepoint'], 16)),
                    label=ico['name'],
                    keywords=ico.get('keywords', [""])[0].replace(",", " ").split()
                )
    
    search_writer.commit()


menus = [
    PPTSymbolsGallery(label="{} ({})".format(label, len(symbollist)), symbols=symbollist, columns=columns)
    for (label, symbollist, columns) in menu_settings
] + [
    # submenu for categories
    bkt.ribbon.DynamicMenu(label="All Categories", get_content=bkt.Callback(get_content_categories))
]
