#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
LINK_PASSAGE_NAME = 'passageName'

HOOK_ORIGINAL_TEXT = 'original'

MACROS_NAME = 'macrosName'
MACROS_VALUE = 'macrosValue'
MACROS_ORIGINAL_TEXT = 'original'

MACRO_DISAPLAY = 'display'

IMAGE_BASE_64 = 'imageBase64'
IMAGE_ORIGINAL = 'original'

class Story:
    
    def __init__(self, story_dict) -> None:        
        self.passages_by_id = {}
        self.passages_by_name = {}
        self.story_dict = story_dict
        for passage in story_dict[STORY_PASSAGES]:
            self.passages_by_id[passage[PASSAGE_ID]] = passage
            if PASSAGE_NAME in passage:
                self.passages_by_name[passage[PASSAGE_NAME]] = passage
        
        first_passage_id = self.story_dict[STORY_FIRST_PASSAGE_ID]
        self.current_passage = self.passages_by_id[first_passage_id]

    def get_name(self) -> str:
        return self.story_dict[STORY_NAME]
    
    def get_clean_text(self) -> str:
        text = self.current_passage[PASSAGE_TEXT]
        
        for macro in self.current_passage[PASSAGE_MACROS]:
            name = macro[MACROS_NAME]
            if (name == MACRO_DISAPLAY):
                value = macro[MACROS_VALUE]
                original_text = macro[MACROS_ORIGINAL_TEXT]
                passage_to_add = self.passages_by_name[value]
                passage_to_add_text = passage_to_add[PASSAGE_TEXT]
                print(f'orig: {text}, macro: {original_text}, replacement: {passage_to_add_text}')
                text = text.replace(original_text, passage_to_add_text)
                self.current_passage[PASSAGE_IMAGES].extend(passage_to_add[PASSAGE_IMAGES])

        for link in self.current_passage[PASSAGE_LINKS]:
            text = text.replace(link[LINK_ORIGINAL_TEXT], '')
        
        for hook in self.current_passage[PASSAGE_HOOKS]:
            text = text.replace(hook[HOOK_ORIGINAL_TEXT], '')
        
        for image in self.current_passage[PASSAGE_IMAGES]:
            text = text.replace(image[IMAGE_ORIGINAL], '')

        return text
    
    def get_image_base64(self):
        return self.current_passage[PASSAGE_IMAGES][0][IMAGE_BASE_64]

    def navigate(self, node_name: str) -> None:
        self.current_passage = self.passages_by_name[node_name]