#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from story import *
from passage import *

TEST_USER = 'test_user'

DEFAULT_ID = '3'

PARAGRAPH_TEST_TEXT = 'paragraph_text'
HOOK_TEST_TEXT = 'hook_text'

class StoryTests(unittest.TestCase):


    def _create_passage(self, id: str = DEFAULT_ID, text: str = "", name: str = "", links = [], hooks = [], macros = [], images = []) -> dict:
        return {PASSAGE_ID: id, PASSAGE_NAME: name, PASSAGE_TEXT: text, PASSAGE_LINKS:links, PASSAGE_HOOKS: hooks, PASSAGE_MACROS: macros, PASSAGE_IMAGES: images}
    
    def _create_macro(self, name: str, value: str, attachedHook: dict = None):
        return {MACROS_NAME: name, MACROS_VALUE: value, MACROS_ORIGINAL_TEXT: f'({name}: "{value}")', MACROS_ATTACHED_HOOK: attachedHook}

    def _create_hidden_hook(self, name: str, text: str = ""):
        return {HOOK_NAME: name, HOOK_TEXT: text, HOOK_ORIGINAL_TEXT: f'|{name})[{text}]', HOOK_IS_HIDDEN: True}

    def _create_dict(self, passages, first_passage_id: str = DEFAULT_ID, story_name: str = "") -> dict:
        return {STORY_NAME: story_name, STORY_FIRST_PASSAGE_ID: first_passage_id, STORY_PASSAGES: passages}

    def test_story_name_showing(self):
        story_name = 'test_name'
        story_dict = self._create_dict(story_name=story_name, passages=[self._create_passage()])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_name(), story_name)

    def test_first_text_showing(self):
        passage = self._create_passage(text = PARAGRAPH_TEST_TEXT)
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEST_TEXT)
    
    def test_links_are_removed_from(self):
        test_link = "[[link|somewhere]]"
        test_text = PARAGRAPH_TEST_TEXT + test_link
        passage = self._create_passage(text = test_text, links=[{LINK_ORIGINAL_TEXT: test_link}])
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEST_TEXT)
    
    def test_hooks_are_changed_to_text(self):
        hook_original = f'[{HOOK_TEST_TEXT}]'
        hook = {HOOK_ORIGINAL_TEXT: hook_original, HOOK_TEXT: HOOK_TEST_TEXT, HOOK_IS_HIDDEN: False}
        test_text = PARAGRAPH_TEST_TEXT + hook_original
        passage = self._create_passage(text = test_text, hooks=[hook])
        story_dict = self._create_dict(passages=[passage])
        story = Story(story_dict, TEST_USER)
        expected_text = PARAGRAPH_TEST_TEXT + HOOK_TEST_TEXT

        self.assertEqual(story.get_clean_text(), expected_text)
    
    def test_navigation_works(self):
        target_name = '9'
        target_id = '10'
        test_link = "[[link|somewhere]]"
        first_passage = self._create_passage(links=[{LINK_ORIGINAL_TEXT: test_link, LINK_DESTINATION_NAME: target_name}])
        target_passage = self._create_passage(target_id, PARAGRAPH_TEST_TEXT, name=target_name)
        story_dict = self._create_dict(passages=[first_passage, target_passage])
        story = Story(story_dict, TEST_USER)

        story.navigate(target_name)

        self.assertEqual(story.get_clean_text(), PARAGRAPH_TEST_TEXT)
    
    def test_display_macro_works(self):
        #Given
        another_passage_name = 'img1'
        another_id = '10'
        another_text = 'another_text'
        another_passage = self._create_passage(id=another_id, text=another_text, name=another_passage_name)

        macro_original = f'({MACRO_DISPLAY}:\"{another_passage_name}\")'
        macro = {MACROS_NAME: MACRO_DISPLAY, MACROS_VALUE: another_passage_name, MACROS_ORIGINAL_TEXT: macro_original}

        test_text = macro_original + PARAGRAPH_TEST_TEXT
        first_passage = self._create_passage(text=test_text, macros=[macro])

        expected_text = another_text + PARAGRAPH_TEST_TEXT

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

        test_text = macro_original + PARAGRAPH_TEST_TEXT
        first_passage = self._create_passage(text=test_text, macros=[macro])

        expected_text = PARAGRAPH_TEST_TEXT

        story_dict = self._create_dict(passages=[first_passage, another_passage])
        story = Story(story_dict, TEST_USER)

        #Then
        self.assertEqual(story.get_clean_text(), expected_text)
        self.assertEqual(story.get_image_base64(), another_image_data)

    def test_links_are_correct(self):
        test_link_text = "link"
        test_link_destination = "somewhere"
        test_link_original_text = f"[[{test_link_text}|{test_link_destination}]]"
        test_text = PARAGRAPH_TEST_TEXT + test_link_original_text
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
        url = story.create_url(MACRO_LINK_REVEAL, macro_value)
        expected_text = f'[{macro_value}]({url})'

        self.assertEqual(story.get_clean_text(), expected_text)

    def test_link_reveal_link_works(self):
        test_hook = f'[{HOOK_TEST_TEXT}]'
        macro_value = "test_value"
        macro = self._create_macro(MACRO_LINK_REVEAL, macro_value, attachedHook={HOOK_ORIGINAL_TEXT: test_hook, HOOK_TEXT: HOOK_TEST_TEXT})
        text = macro[MACROS_ORIGINAL_TEXT] + test_hook
        test_passage = self._create_passage(text=text, macros=[macro])
        story_dict = self._create_dict(passages=[test_passage])
        story = Story(story_dict, TEST_USER)
        data = story._create_url_data(MACRO_LINK_REVEAL, macro_value)
        expected_text = macro_value + HOOK_TEST_TEXT

        story.navigate_by_deeplink(data)

        self.assertEqual(story.get_clean_text(), expected_text)
    
    def test_show_macro_is_working(self):
        hidden_hook_name = "hook_name"
        hidden_hook = self._create_hidden_hook(hidden_hook_name, HOOK_TEST_TEXT)

        show_macro = self._create_macro(name='show', value=f'?{hidden_hook_name}')
        text = show_macro[MACROS_ORIGINAL_TEXT] + hidden_hook[HOOK_ORIGINAL_TEXT]

        passage = self._create_passage(text=text, macros=[show_macro], hooks=[hidden_hook])
        story = Story(self._create_dict(passages=[passage]), TEST_USER)

        self.assertEqual(story.get_clean_text(), HOOK_TEST_TEXT)
    
    def test_show_macro_in_hook_works(self):
        # "[(show: ?hobert)].\n|hobert)[\n(His name was actually Hobert)]"
        hidden_hook_name = "hook_name"
        hidden_hook_text = "hook_text"
        macro = self._create_macro(MACRO_SHOW, f'?{hidden_hook_name}')
        hook = {HOOK_TEXT: macro[MACROS_ORIGINAL_TEXT], HOOK_ORIGINAL_TEXT: f'[{macro[MACROS_ORIGINAL_TEXT]}]', HOOK_MACROS: [macro], HOOK_IS_HIDDEN: False}
        hidden_hook = self._create_hidden_hook(hidden_hook_name, hidden_hook_text)
        passage_text = hook[HOOK_ORIGINAL_TEXT] + hidden_hook[HOOK_ORIGINAL_TEXT]
        passage = self._create_passage(text=passage_text, hooks=[hook, hidden_hook])
        story = Story(self._create_dict(passages=[passage]), TEST_USER)

        self.assertEqual(story.get_clean_text(), hidden_hook_text)

if __name__ == '__main__':
    unittest.main()