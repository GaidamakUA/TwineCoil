#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
import json, base64
from passage import Passage
from telegram.utils import helpers

STORY_NAME = 'name'
STORY_PASSAGES = 'passages'
STORY_FIRST_PASSAGE_ID = "startNode"

IMAGE_BASE_64 = 'imageBase64'

JSON_NAME = 'name'
JSON_VALUE = 'value'

class Story:
    
    def __init__(self, story_dict: dict, username: str) -> None:        
        self.passages_by_id = {}
        self.passages_by_name = {}
        self.story_dict = story_dict
        for passage_dict in story_dict[STORY_PASSAGES]:
            passage = Passage(passage_dict)
            self.passages_by_id[passage.id] = passage
            if passage.name != None:
                self.passages_by_name[passage.name] = passage
        
        first_passage_id = self.story_dict[STORY_FIRST_PASSAGE_ID]
        self.current_passage: Passage = self.passages_by_id[first_passage_id]
        self.username = username

    def get_name(self) -> str:
        return self.story_dict[STORY_NAME]
    
    def get_clean_text(self) -> str:
        return self.current_passage.get_clean_text(self.passages_by_name, self)

    def get_image_base64(self) -> str:
        if len(self.current_passage.images) > 0:
            return self.current_passage.images[0][IMAGE_BASE_64]

    def navigate(self, node_name: str) -> None:
        self.current_passage = self.passages_by_name[node_name]
    
    def navigate_by_deeplink(self, data: str) -> None:
        json_string = self._base64_urlsafe_decode(data)
        json_data = json.loads(json_string)
        name = json_data[JSON_NAME]
        value = json_data[JSON_VALUE]
        self.current_passage.navigate_by_macro(name, value)
    
    def get_links(self) -> List:
        return self.current_passage.get_links()
    
    def create_url(self, link_name: str, link_value: str) -> str:
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