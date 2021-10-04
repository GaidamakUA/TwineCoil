#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List
from telegram.utils import helpers
import json
import base64

STORY_NAME = 'name'
STORY_PASSAGES = 'passages'
STORY_FIRST_PASSAGE_ID = "startNode"

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

HOOK_NAME = 'hookName'
HOOK_ORIGINAL_TEXT = 'original'
HOOK_TEXT = 'hookText'
HOOK_IS_HIDDEN = 'isHidden'

MACROS_NAME = 'macrosName'
MACROS_VALUE = 'macrosValue'
MACROS_ORIGINAL_TEXT = 'original'
MACROS_ATTACHED_HOOK = 'attachedHook'

MACRO_DISPLAY = 'display'
MACRO_LINK_REVEAL = 'link-reveal'
MACRO_SHOW = 'show'

IMAGE_BASE_64 = 'imageBase64'
IMAGE_ORIGINAL = 'original'

JSON_NAME = 'name'
JSON_VALUE = 'value'

@dataclass
class Link:
    link_text: str
    destination_name: str

class Story:
    
    def __init__(self, story_dict: dict, username: str) -> None:        
        self.passages_by_id = {}
        self.passages_by_name = {}
        self.story_dict = story_dict
        for passage in story_dict[STORY_PASSAGES]:
            self.passages_by_id[passage[PASSAGE_ID]] = passage
            if PASSAGE_NAME in passage:
                self.passages_by_name[passage[PASSAGE_NAME]] = passage
        
        first_passage_id = self.story_dict[STORY_FIRST_PASSAGE_ID]
        self.current_passage = self.passages_by_id[first_passage_id]
        self.username = username

    def get_name(self) -> str:
        return self.story_dict[STORY_NAME]
    
    def get_clean_text(self) -> str:
        text = self.current_passage[PASSAGE_TEXT]
        
        for macro in self.current_passage[PASSAGE_MACROS]:
            name = macro[MACROS_NAME]
            value = macro[MACROS_VALUE]
            original_text = macro[MACROS_ORIGINAL_TEXT]

            if (name == MACRO_DISPLAY):
                passage_to_add = self.passages_by_name[value]
                passage_to_add_text = passage_to_add[PASSAGE_TEXT]
                text = text.replace(original_text, passage_to_add_text)
                self.current_passage[PASSAGE_IMAGES].extend(passage_to_add[PASSAGE_IMAGES])
            if (name == MACRO_LINK_REVEAL):
                url = self._create_url(MACRO_LINK_REVEAL, value)
                url_text = f'[{value}]({url})'
                text = text.replace(original_text, url_text)

                hook = macro[MACROS_ATTACHED_HOOK]
                hook_original = hook[HOOK_ORIGINAL_TEXT]
                text = text.replace(hook_original, "")
            if (name == MACRO_SHOW):
                hook_name = value[1:]
                for hook in self.current_passage[PASSAGE_HOOKS]:
                    if hook[HOOK_NAME] == hook_name:
                        hook[HOOK_IS_HIDDEN] = False
                text = text.replace(original_text, "")


        for link in self.current_passage[PASSAGE_LINKS]:
            text = text.replace(link[LINK_ORIGINAL_TEXT], '')
        
        for hook in self.current_passage[PASSAGE_HOOKS]:
            if hook[HOOK_IS_HIDDEN]:
                text = text.replace(hook[HOOK_ORIGINAL_TEXT], '')
            else:
                text = text.replace(hook[HOOK_ORIGINAL_TEXT], hook[HOOK_TEXT])
        
        for image in self.current_passage[PASSAGE_IMAGES]:
            text = text.replace(image[IMAGE_ORIGINAL], '')

        return text
    
    def get_image_base64(self) -> str:
        if len(self.current_passage[PASSAGE_IMAGES]) > 0:
            return self.current_passage[PASSAGE_IMAGES][0][IMAGE_BASE_64]

    def navigate(self, node_name: str) -> None:
        self.current_passage = self.passages_by_name[node_name]
    
    def navigate_by_deeplink(self, data: str) -> None:
        json_string = self._base64_urlsafe_decode(data)
        json_data = json.loads(json_string)
        name = json_data[JSON_NAME]
        value = json_data[JSON_VALUE]
        for macro in self.current_passage[PASSAGE_MACROS]:
            if name == MACRO_LINK_REVEAL and macro[MACROS_NAME] == MACRO_LINK_REVEAL and macro[MACROS_VALUE] == value:
                text = self.current_passage[PASSAGE_TEXT]
                replacement = value + macro[MACROS_ATTACHED_HOOK][HOOK_TEXT]
                text = text.replace(macro[MACROS_ORIGINAL_TEXT], replacement)
                self.current_passage[PASSAGE_TEXT] = text
    
    def get_links(self) -> List[Link]:
        links = []
        for json_link in self.current_passage[PASSAGE_LINKS]:
            links.append(Link(link_text=json_link[LINK_TEXT], destination_name=json_link[LINK_DESTINATION_NAME]))
        return links
    
    def _create_url(self, link_name: str, link_value: str) -> str:
        data = self._create_url_data(link_name=link_name, link_value=link_value)
        return helpers.create_deep_linked_url(self.username, data)

    def _create_url_data(self, link_name: str, link_value: str) -> str:
        json_data = json.dumps({JSON_NAME: link_name, JSON_VALUE: link_value})
        return self._base64_urlsafe_encode(json_data)

    def _base64_urlsafe_encode(self, string):
        """
        Removes any `=` used as padding from the encoded string.
        """
        encoded = base64.urlsafe_b64encode(string.encode('ascii'))
        return encoded.rstrip(b"=").decode('ascii')

    def _base64_urlsafe_decode(self, string):
        """
        Adds back in the required padding before decoding.
        """
        padding = 4 - (len(string) % 4)
        string = string + ("=" * padding)
        return base64.urlsafe_b64decode(string.encode('ascii')).decode('ascii')