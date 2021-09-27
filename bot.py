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
        json_data = base64_decode(payload[0])
        data = json.loads(json_data)
        node_name = data["node"]
        link = data[LINK_REVEAL]

        show_node(node_name, update, context)
    else:
        context.user_data.clear()
        context.user_data[STORY] = Story(selected_story)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Name: {story['name']}", reply_markup=reply_markup)

def get_image_bytes(image_node_name):
    image_node = nodes_by_name[image_node_name]
    node_text = image_node['text']
    image_base64 = node_text.replace("<img src='data:image/png;base64,", "").replace("'/>", "")
    return base64.b64decode(image_base64.encode('ascii'))#base64.decodebytes(image_base64)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    node_name = query.data

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.delete_message()

    show_node(node_name, update, context)

def show_node(node_name: str, update: Update, context: CallbackContext, macros: str = None):
    username = context.bot.username
    node = nodes_by_name[node_name]
    if macros == None:
        text = node["cleanText"]
        context.user_data[CURRENT_TEXT] = node["text"]
    else:
        text = context.user_data[CURRENT_TEXT]
    
    # If start -> drop data
    # If no macro -> show clear text + save text
    # If macro -> get saved text, mutate text, regenerate clear text

    keyboard = []
    for link in node['links']:
        keyboard.append([InlineKeyboardButton(link['linkText'], callback_data=link['passageName'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    macros = node["macros"]
    image_bytes = None
    for macro in macros:
        if macro["macrosName"] == "display":
            text = text.replace(macro["original"], "")
            image_bytes = get_image_bytes(macro["macrosValue"])
        elif macro["macrosName"] == "link-reveal":
            json_data = json.dumps({"node": node_name, LINK_REVEAL: macro["macrosValue"]})
            data = base64_encode(json_data)
            url = helpers.create_deep_linked_url(username, data)
            text = text.replace(macro["original"], f'[{macro["macrosValue"]}]({url})')

    if image_bytes == None:
        update.effective_chat.send_message(text=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        update.effective_chat.send_photo(image_bytes, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

def handle_changer_macro(text: str, macro: str) -> str:
    if macro == "link-reveal":
        pass

def base64_encode(string):
    """
    Removes any `=` used as padding from the encoded string.
    """
    encoded = base64.urlsafe_b64encode(string.encode('ascii'))
    return encoded.rstrip(b"=").decode('ascii')


def base64_decode(string):
    """
    Adds back in the required padding before decoding.
    """
    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    return base64.urlsafe_b64decode(string.encode('ascii')).decode('ascii')

selected_story = {}
with open('SPACE_FROG.json') as f:
   selected_story = json.load(f)

updater = Updater('2041075360:AAHKscKQNqv59YHxC4PdQc_khn7lzGYz8_k')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()