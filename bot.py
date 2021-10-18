#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

# Simple Bot to reply to Telegram messages.First, a few handler functions are defined. Then, those functions are passed to
# the Dispatcher and registered at their respective places.
# Then, the bot is started and runs until we press Ctrl-C on the command line.Usage:
# Basic Echobot example, repeats messages.
# Press Ctrl-C on the command line or send a signal to the process to stop the
# bot.
import json
import base64
from os.path import exists
from pathlib import Path
from story import Story
from link import Link
import sys
from typing import List

from telegram import ParseMode, Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Filters
from telegram.utils import helpers

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

STORY = "story"

def start(update: Update, context: CallbackContext) -> None:
    payload = context.args
    if len(payload) > 0:
        data = payload[0]
        story: Story = context.user_data[STORY]
        story.navigate_by_deeplink(data)
    else:
        context.user_data.clear()
        username = context.bot.username
        context.user_data[STORY] = Story(selected_story, username)
    update_message(update, context)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    node_name = query.data

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.delete_message()

    story: Story = context.user_data[STORY]
    story.navigate(node_name)

    update_message(update, context)

def update_message(update: Update, context: CallbackContext):
    story: Story = context.user_data[STORY]

    text = story.get_clean_text()
    links: List[Link] = story.get_links()

    keyboard = []
    for link in links:
        keyboard.append([InlineKeyboardButton(link.link_text, callback_data=link.destination_name)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = story.get_clean_text()
    image_base64 = story.get_image_base64()
    image_bytes = None
    if image_base64 != None:
        image_bytes = base64.b64decode(image_base64.encode('ascii'))

    if image_bytes == None:
        update.effective_chat.send_message(text=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        update.effective_chat.send_photo(image_bytes, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

selected_story = {}
with open('SPACE_FROG.json') as f:
   selected_story = json.load(f)

updater = Updater(sys.argv[1])

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()