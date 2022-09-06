# -*- encoding: utf-8 -*-
'''
_______________________    ________________
__  __ \__  /____  _/_ |  / /_  __ \_  ___/
_  / / /_  /  __  / __ | / /_  / / /____ \
/ /_/ /_  /____/ /  __ |/ / / /_/ /____/ /
\____/ /_____/___/  _____/  \____/ /____/

@File      :   OlivOS/virtualTerminalSDK.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

from enum import IntEnum
import sys
import json
import traceback
import requests as req
import time

import OlivOS

class bot_info_T(object):
    def __init__(self, id = -1, access_token = None, model = 'private'):
        self.id = id
        self.access_token = access_token
        self.model = model
        self.debug_mode = False
        self.debug_logger = None

def get_SDK_bot_info_from_Plugin_bot_info(plugin_bot_info):
    res = bot_info_T(
        plugin_bot_info.id,
        plugin_bot_info.post_info.access_token
    )
    res.debug_mode = plugin_bot_info.debug_mode
    if plugin_bot_info.platform['model'] == 'public':
        res.model = 'public'
    return res

def get_SDK_bot_info_from_Event(target_event):
    res = get_SDK_bot_info_from_Plugin_bot_info(target_event.bot_info)
    return res

class event(object):
    def __init__(self, payload_obj = None, bot_info = None):
        self.payload = payload_obj
        self.platform = {}
        self.platform['sdk'] = 'terminal_link'
        self.platform['platform'] = 'terminal'
        self.platform['model'] = 'default'
        self.active = False
        if self.payload != None:
            self.active = True
        self.base_info = {}
        if self.active:
            self.base_info['time'] = int(time.time())
            self.base_info['self_id'] = bot_info.id
            self.base_info['token'] = bot_info.post_info.access_token
            self.base_info['post_type'] = None

def get_Event_from_SDK(target_event):
    global sdkSubSelfInfo
    target_event.base_info['time'] = target_event.sdk_event.base_info['time']
    target_event.base_info['self_id'] = str(target_event.sdk_event.base_info['self_id'])
    target_event.base_info['type'] = target_event.sdk_event.base_info['post_type']
    target_event.platform['sdk'] = target_event.sdk_event.platform['sdk']
    target_event.platform['platform'] = target_event.sdk_event.platform['platform']
    target_event.platform['model'] = target_event.sdk_event.platform['model']
    target_event.plugin_info['message_mode_rx'] = 'olivos_string'
    plugin_event_bot_hash = OlivOS.API.getBotHash(
        bot_id = target_event.base_info['self_id'],
        platform_sdk = target_event.platform['sdk'],
        platform_platform = target_event.platform['platform'],
        platform_model = target_event.platform['model']
    )
    message_obj = OlivOS.messageAPI.Message_templet(
        'olivos_string',
        target_event.sdk_event.payload.key['data']['data']
    )
    if message_obj.active:
        target_event.active = True
        target_event.plugin_info['func_type'] = 'group_message'
        target_event.data = target_event.group_message(
            str(88888888),
            str(88888888),
            message_obj,
            'group'
        )
        target_event.data.message_sdk = message_obj
        target_event.data.message_id = str(88888888)
        target_event.data.raw_message = message_obj
        target_event.data.raw_message_sdk = message_obj
        target_event.data.font = None
        target_event.data.sender['user_id'] = str(88888888)
        target_event.data.sender['nickname'] = '仑质'
        target_event.data.sender['id'] = str(88888888)
        target_event.data.sender['name'] = '仑质'
        target_event.data.sender['sex'] = 'unknown'
        target_event.data.sender['age'] = 0
        target_event.data.sender['role'] = 'owner'
        target_event.data.host_id = None

#支持OlivOS API调用的方法实现
class event_action(object):
    def send_msg(target_event, message, control_queue):
        plugin_event_bot_hash = OlivOS.API.getBotHash(
            bot_id = target_event.base_info['self_id'],
            platform_sdk = target_event.platform['sdk'],
            platform_platform = target_event.platform['platform'],
            platform_model = target_event.platform['model']
        )
        send_log_event(plugin_event_bot_hash, message, 'BOT', control_queue)

def sendControlEventSend(action, data, control_queue):
    if control_queue != None:
        control_queue.put(
            OlivOS.API.Control.packet(
                action,
                data
            ),
            block = False
        )

def send_log_event(hash, data, name, control_queue):
    sendControlEventSend('send', {
            'target': {
                'type': 'nativeWinUI'
            },
            'data': {
                'action': 'virtual_terminal',
                'event': 'log',
                'hash': hash,
                'data': data,
                'name': name
            }
        },
        control_queue
    )