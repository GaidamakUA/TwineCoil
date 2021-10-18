#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
from macro import *
from link import Link

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

class Passage:

    def __init__(self, paragraph_dict: dict, link_creator):
        self.id = paragraph_dict[PASSAGE_ID]
        if PASSAGE_NAME in paragraph_dict:
            self.name = paragraph_dict[PASSAGE_NAME]
        self.text = paragraph_dict[PASSAGE_TEXT]
        self.links_json = paragraph_dict[PASSAGE_LINKS]
        self.hooks = paragraph_dict[PASSAGE_HOOKS]
        self.macros = paragraph_dict[PASSAGE_MACROS]
        self.images = paragraph_dict[PASSAGE_IMAGES]
        self.link_creator = link_creator

        self._preprocess_static()
    
    def _preprocess_static(self):
        self.links = []
        for link_json in self.links_json:
            self.text = self.text.replace(link_json[LINK_ORIGINAL_TEXT], '')
            self.links.append(Link(link_text=link_json[LINK_TEXT], destination_name=link_json[LINK_DESTINATION_NAME]))
        
        for image in self.images:
            self.text = self.text.replace(image[IMAGE_ORIGINAL], '')

    def get_links(self) -> List[Link]:
        return self.links
    
    def get_clean_text(self, passages_by_name: dict) -> str:
        # The idea is to handle hook/macro while there are hooks and macros.
        # Operations will have order
        # Show macro before hidden hooks

        self._process_active_hooks()
        self._process_macros(passages_by_name)
        self._process_active_hooks()
        self._hide_hidden_hooks()

        return self.text
    
    def _process_macros(self, passages_by_name: dict):
        for macro in self.macros:
            name = macro[MACROS_NAME]
            value = macro[MACROS_VALUE]
            original_text = macro[MACROS_ORIGINAL_TEXT]

            if (name == MACRO_SHOW):
                hook_name = value[1:]
                for hook in self.hooks:
                    if hook[HOOK_NAME] == hook_name:
                        hook[HOOK_IS_HIDDEN] = False
                self.text = self.text.replace(original_text, "")
                self.macros.remove(macro)
            if (name == MACRO_DISPLAY):
                passage_to_add: Passage = passages_by_name[value]
                self.text = self.text.replace(original_text, passage_to_add.text)
                self.images.extend(passage_to_add.images)
            if (name == MACRO_LINK_REVEAL):
                url = self.link_creator.create_url(MACRO_LINK_REVEAL, value)
                url_text = f'[{value}]({url})'
                self.text = self.text.replace(original_text, url_text)

                hook = macro[MACROS_ATTACHED_HOOK]
                hook_original = hook[HOOK_ORIGINAL_TEXT]
                self.text = self.text.replace(hook_original, "")
    
    def _process_active_hooks(self):
        for hook in self.hooks:
            if not hook[HOOK_IS_HIDDEN]:
                self.text = self.text.replace(hook[HOOK_ORIGINAL_TEXT], hook[HOOK_TEXT])
                self.hooks.remove(hook)
                if HOOK_MACROS in hook:
                    self.macros.extend(hook[HOOK_MACROS])

    def _hide_hidden_hooks(self):
        for hook in self.hooks:
            if hook[HOOK_IS_HIDDEN]:
                self.text = self.text.replace(hook[HOOK_ORIGINAL_TEXT], '')
    
    def navigate_by_macro(self, name: str, value: str):
        for macro in self.macros:
            if name == MACRO_LINK_REVEAL and macro[MACROS_NAME] == MACRO_LINK_REVEAL and macro[MACROS_VALUE] == value:
                url = self.link_creator.create_url(MACRO_LINK_REVEAL, value)
                url_text = f'[{value}]({url})'
                replacement = value + macro[MACROS_ATTACHED_HOOK][HOOK_TEXT]
                self.text = self.text.replace(url_text, replacement)
                hook = macro[MACROS_ATTACHED_HOOK]
                self.hooks.append(hook)


