#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List
from macro import *

PASSAGE_ID = 'id'
PASSAGE_NAME = 'name'
PASSAGE_TEXT = 'text'
PASSAGE_LINKS = 'links'
PASSAGE_HOOKS = 'hooks'
PASSAGE_MACROS = 'macros'
PASSAGE_IMAGES = 'image'

LINK_ORIGINAL_TEXT = 'original'
LINK_TEXT = 'linkText'
LINK_DESTINATION_NAME = 'passageName'

IMAGE_ORIGINAL = 'original'

HOOK_NAME = 'hookName'
HOOK_ORIGINAL_TEXT = 'original'
HOOK_TEXT = 'hookText'
HOOK_IS_HIDDEN = 'isHidden'
HOOK_MACROS = 'macros'

@dataclass
class Link:
    link_text: str
    destination_name: str

class Passage:

    def __init__(self, paragraph_dict: dict):
        self.id = paragraph_dict[PASSAGE_ID]
        if PASSAGE_NAME in paragraph_dict:
            self.name = paragraph_dict[PASSAGE_NAME]
        self.text = paragraph_dict[PASSAGE_TEXT]
        self.links = paragraph_dict[PASSAGE_LINKS]
        self.hooks = paragraph_dict[PASSAGE_HOOKS]
        self.macros = paragraph_dict[PASSAGE_MACROS]
        self.images = paragraph_dict[PASSAGE_IMAGES]

        self._preprocess_static()
    
    def _preprocess_static(self):
        for link in self.links:
            print(f'link: {link}')
            self.text = self.text.replace(link[LINK_ORIGINAL_TEXT], '')
        
        for image in self.images:
            self.text = self.text.replace(image[IMAGE_ORIGINAL], '')

    def get_links(self) -> List[Link]:
        links = []
        for json_link in self.links:
            links.append(Link(link_text=json_link[LINK_TEXT], destination_name=json_link[LINK_DESTINATION_NAME]))
        return links
    
    def get_clean_text(self, passages_by_name: dict, link_creator) -> str:
        text = self.text
        # The idea is to handle hook/macro while there are hooks and macros.
        # And move logic to Paragraph object
        # Operations will have order
        # Show macro before hidden hooks
        for hook in self.hooks:
            if hook[HOOK_IS_HIDDEN]:
                text = text.replace(hook[HOOK_ORIGINAL_TEXT], '')
            else:
                text = text.replace(hook[HOOK_ORIGINAL_TEXT], hook[HOOK_TEXT])
                self.hooks.remove(hook)
                if HOOK_MACROS in hook:
                    self.macros.extend(hook[HOOK_MACROS])

        for macro in self.macros:
            name = macro[MACROS_NAME]
            value = macro[MACROS_VALUE]
            original_text = macro[MACROS_ORIGINAL_TEXT]

            if (name == MACRO_SHOW):
                hook_name = value[1:]
                for hook in self.hooks:
                    if hook[HOOK_NAME] == hook_name:
                        hook[HOOK_IS_HIDDEN] = False
                text = text.replace(original_text, "")
                self.macros.remove(macro)
            if (name == MACRO_DISPLAY):
                passage_to_add = passages_by_name[value]
                passage_to_add_text = self.text
                text = text.replace(original_text, passage_to_add_text)
                self.images.extend(passage_to_add.images)
            if (name == MACRO_LINK_REVEAL):
                url = link_creator.create_url(MACRO_LINK_REVEAL, value)
                url_text = f'[{value}]({url})'
                text = text.replace(original_text, url_text)

                hook = macro[MACROS_ATTACHED_HOOK]
                hook_original = hook[HOOK_ORIGINAL_TEXT]
                text = text.replace(hook_original, "")

        return text
    
    def navigate_by_macro(self, name: str, value: str):
        for macro in self.macros:
            if name == MACRO_LINK_REVEAL and macro[MACROS_NAME] == MACRO_LINK_REVEAL and macro[MACROS_VALUE] == value:
                text = self.text
                replacement = value + macro[MACROS_ATTACHED_HOOK][HOOK_TEXT]
                text = text.replace(macro[MACROS_ORIGINAL_TEXT], replacement)
                self.text = text


