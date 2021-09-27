#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from story import *

class StoryTests(unittest.TestCase):

    def _create_passage(self, id: str, text: str = "", name: str = "", links = [], hooks = [], macros = [], images = []) -> dict:
        return {PASSAGE_ID: id, PASSAGE_NAME: name, PASSAGE_TEXT: text, PASSAGE_LINKS:links, PASSAGE_HOOKS: hooks, PASSAGE_MACROS: macros, PASSAGE_IMAGES: images}
    
    def _create_dict(self, passages, first_passage_id: str, story_name: str = "") -> dict:
        return {STORY_NAME: story_name, STORY_FIRST_PASSAGE_ID: first_passage_id, STORY_PASSAGES: passages}

    def test_story_name_showing(self):
        test_name = "test_name"
        test_id = "3"
        story_dict = self._create_dict(story_name=test_name, first_passage_id=test_id, passages=[self._create_passage(test_id)])
        story = Story(story_dict)

        self.assertEqual(story.get_name(), test_name)

    def test_first_text_showing(self):
        test_text = "test_text"
        test_id = "3"
        passage = self._create_passage(test_id, test_text)
        story_dict = self._create_dict(first_passage_id=test_id, passages=[passage])
        story = Story(story_dict)

        self.assertEqual(story.get_clean_text(), test_text)
    
    def test_links_are_removed_from(self):
        test_id = "3"
        test_link = "[[link|somewhere]]"
        test_clean_text = "test_text"
        test_text = test_clean_text + test_link
        passage = self._create_passage(test_id, test_text, links=[{LINK_ORIGINAL_TEXT: test_link}])
        story_dict = self._create_dict(first_passage_id=test_id, passages=[passage])
        story = Story(story_dict)

        self.assertEqual(story.get_clean_text(), test_clean_text)
    
    def test_hooks_are_remomoved_from_text(self):
        test_id = "3"
        test_hook = "[test_hook]"
        test_clean_text = "test_text"
        test_text = test_clean_text + test_hook
        passage = self._create_passage(test_id, test_text, hooks=[{HOOK_ORIGINAL_TEXT: test_hook}])
        story_dict = self._create_dict(first_passage_id=test_id, passages=[passage])
        story = Story(story_dict)

        self.assertEqual(story.get_clean_text(), test_clean_text)
    
    def test_navigation_works(self):
        target_text = "test_text"
        first_id = '3'
        target_name = '9'
        target_id = '10'
        first_passage = self._create_passage(first_id, "", links=[{LINK_PASSAGE_NAME: target_name}])
        target_passage = self._create_passage(target_id, target_text, name=target_name)
        story_dict = self._create_dict(first_passage_id=first_id, passages=[first_passage, target_passage])
        story = Story(story_dict)

        story.navigate(target_name)

        self.assertEqual(story.get_clean_text(), target_text)
    
    def test_display_macro_works(self):
        #Given
        another_passage_name = 'img1'
        another_id = '10'
        another_text = 'another_text'
        another_passage = self._create_passage(another_id, another_text, name=another_passage_name)

        macro_original = f'({MACRO_DISAPLAY}:\"{another_passage_name}\")'
        macro = {MACROS_NAME: MACRO_DISAPLAY, MACROS_VALUE: another_passage_name, MACROS_ORIGINAL_TEXT: macro_original}

        test_clean_text = 'Once upon a time'
        test_text = macro_original + test_clean_text
        test_id = '3'
        first_passage = self._create_passage(test_id, test_text, macros=[macro])

        expected_text = another_text + test_clean_text

        story_dict = self._create_dict(first_passage_id=test_id, passages=[first_passage, another_passage])
        story = Story(story_dict)

        #Then
        self.assertEqual(story.get_clean_text(), expected_text)

    def test_showing_image_works(self):
        #Given
        another_passage_name = 'img1'
        another_id = '10'
        another_image_data = 'image_data'
        another_image_original = 'some_text' + another_image_data
        another_text = another_image_original
        another_passage = self._create_passage(another_id, another_text, name=another_passage_name, images=[{IMAGE_BASE_64: another_image_data, IMAGE_ORIGINAL: another_image_original}])

        macro_original = f'({MACRO_DISAPLAY}:\"{another_passage_name}\")'
        macro = {MACROS_NAME: MACRO_DISAPLAY, MACROS_VALUE: another_passage_name, MACROS_ORIGINAL_TEXT: macro_original}

        test_clean_text = 'Once upon a time'
        test_text = macro_original + test_clean_text
        test_id = '3'
        first_passage = self._create_passage(test_id, test_text, macros=[macro])

        expected_text = test_clean_text

        story_dict = self._create_dict(first_passage_id=test_id, passages=[first_passage, another_passage])
        story = Story(story_dict)

        #Then
        self.assertEqual(story.get_clean_text(), expected_text)
        self.assertEqual(story.get_image_base64(), another_image_data)

    def test_link_reveal_macro_works(self):
        pass

if __name__ == '__main__':
    unittest.main()