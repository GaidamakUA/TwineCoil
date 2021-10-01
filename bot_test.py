#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from story import *

TEST_USER = 'test_user'

DEFAULT_ID = '3'

PARAGRAPH_TEXT = 'test_text'

class StoryTests(unittest.TestCase):


    def _create_passage(self, id: str = DEFAULT_ID, text: str = "", name: str = "", links = [], hooks = [], macros = [], images = []) -> dict:
        return {PASSAGE_ID: id, PASSAGE_NAME: name, PASSAGE_TEXT: text, PASSAGE_LINKS:links, PASSAGE_HOOKS: hooks, PASSAGE_MACROS: macros, PASSAGE_IMAGES: images}
    
    def _create_macro(self, name: str, value: str, attachedHook: dict = None):
        return {MACROS_NAME: name, MACROS_VALUE: value, MACROS_ORIGINAL_TEXT: f'({name}: "{value}")', MACROS_ATTACHED_HOOK: attachedHook}

    def _create_dict(self, passages, first_passage_id: str = DEFAULT_ID, story_name: str = "") -> dict:
        return {STORY_NAME: story_name, STORY_FIRST_PASSAGE_ID: first_passage_id, STORY_PASSAGES: passages}

    def test_story_name_showing(self):
        story_name = 'test_name'
        story_dict = self._create_dict(story_name=story_name, passages=[self._create_passage()])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_name(), story_name)

    def test_first_text_showing(self):
        passage = self._create_passage(text = PARAGRAPH_TEXT)
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEXT)
    
    def test_links_are_removed_from(self):
        test_link = "[[link|somewhere]]"
        test_text = PARAGRAPH_TEXT + test_link
        passage = self._create_passage(text = test_text, links=[{LINK_ORIGINAL_TEXT: test_link}])
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEXT)
    
    def test_hooks_are_remomoved_from_text(self):
        test_hook = "[test_hook]"
        test_text = PARAGRAPH_TEXT + test_hook
        passage = self._create_passage(text = test_text, hooks=[{HOOK_ORIGINAL_TEXT: test_hook}])
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEXT)
    
    def test_navigation_works(self):
        target_name = '9'
        target_id = '10'
        first_passage = self._create_passage(links=[{LINK_DESTINATION_NAME: target_name}])
        target_passage = self._create_passage(target_id, PARAGRAPH_TEXT, name=target_name)
        story_dict = self._create_dict(passages=[first_passage, target_passage])
        story = Story(story_dict, TEST_USER)

        story.navigate(target_name)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEXT)
    
    def test_display_macro_works(self):
        #Given
        another_passage_name = 'img1'
        another_id = '10'
        another_text = 'another_text'
        another_passage = self._create_passage(id=another_id, text=another_text, name=another_passage_name)

        macro_original = f'({MACRO_DISPLAY}:\"{another_passage_name}\")'
        macro = {MACROS_NAME: MACRO_DISPLAY, MACROS_VALUE: another_passage_name, MACROS_ORIGINAL_TEXT: macro_original}

        test_text = macro_original + PARAGRAPH_TEXT
        first_passage = self._create_passage(text=test_text, macros=[macro])

        expected_text = another_text + PARAGRAPH_TEXT

        story_dict = self._create_dict(passages=[first_passage, another_passage])
        story = Story(story_dict, TEST_USER)

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

        macro_original = f'({MACRO_DISPLAY}:\"{another_passage_name}\")'
        macro = {MACROS_NAME: MACRO_DISPLAY, MACROS_VALUE: another_passage_name, MACROS_ORIGINAL_TEXT: macro_original}

        test_text = macro_original + PARAGRAPH_TEXT
        first_passage = self._create_passage(text=test_text, macros=[macro])

        expected_text = PARAGRAPH_TEXT

        story_dict = self._create_dict(passages=[first_passage, another_passage])
        story = Story(story_dict, TEST_USER)

        #Then
        self.assertEqual(story.get_clean_text(), expected_text)
        self.assertEqual(story.get_image_base64(), another_image_data)

    def test_links_are_correct(self):
        test_link_text = "link"
        test_link_destination = "somewhere"
        test_link_original_text = f"[[{test_link_text}|{test_link_destination}]]"
        test_text = PARAGRAPH_TEXT + test_link_original_text
        test_link = {LINK_ORIGINAL_TEXT: test_link_original_text, LINK_DESTINATION_NAME: test_link_destination, LINK_TEXT: test_link_text}
        passage = self._create_passage(text=test_text, links=[test_link])
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        links = story.get_links()
        link: Link = links[0]
        self.assertEqual(len(links), 1)
        self.assertEqual(link.link_text, test_link_text)
        self.assertEqual(link.destination_name, test_link_destination)
    
    def test_get_image_returns_none_if_no_image_present(self):
        story_dict = self._create_dict(passages=[self._create_passage()])
        story = Story(story_dict, TEST_USER)

        self.assertIsNone(story.get_image_base64())

    def test_link_reveal_hides_inner_text(self):
        test_hook = "[test]"
        macro_value = "test_value"
        macro = self._create_macro(MACRO_LINK_REVEAL, macro_value, attachedHook={HOOK_ORIGINAL_TEXT: test_hook})
        text = macro[MACROS_ORIGINAL_TEXT] + test_hook
        test_passage = self._create_passage(text=text, macros=[macro])
        story_dict = self._create_dict(passages=[test_passage])
        story = Story(story_dict, TEST_USER)
        url = story._create_url(MACRO_LINK_REVEAL, macro_value)
        expected_text = f'[{macro_value}]({url})'

        self.assertEqual(story.get_clean_text(), expected_text)

    def test_link_reveal_link_works(self):
        hook_text = 'test'
        test_hook = f'[{hook_text}]'
        macro_value = "test_value"
        macro = self._create_macro(MACRO_LINK_REVEAL, macro_value, attachedHook={HOOK_ORIGINAL_TEXT: test_hook, HOOK_TEXT: hook_text})
        text = macro[MACROS_ORIGINAL_TEXT] + test_hook
        test_passage = self._create_passage(text=text, macros=[macro])
        story_dict = self._create_dict(passages=[test_passage])
        story = Story(story_dict, TEST_USER)
        data = story._create_url_data(MACRO_LINK_REVEAL, macro_value)
        expected_text = macro_value + hook_text

        story.navigate_by_deeplink(data)

        self.assertEqual(story.get_clean_text(), expected_text)

if __name__ == '__main__':
    unittest.main()