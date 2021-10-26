# -*- encoding: utf-8 -*-
'''
_______________________    ________________
__  __ \__  /____  _/_ |  / /_  __ \_  ___/
_  / / /_  /  __  / __ | / /_  / / /____ \
/ /_/ /_  /____/ /  __ |/ / / /_/ /____/ /
\____/ /_____/___/  _____/  \____/ /____/

@File      :   OlivOS/API.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import sys
import json
import multiprocessing
import hashlib

from functools import wraps

import OlivOS

OlivOS_Version = OlivOS.infoAPI.OlivOS_Version
mod_global_name = sys.modules[__name__]


class Control(object):
    def __init__(self, name, init_list, control_queue, scan_interval):
        self.name = name
        self.init_list = init_list
        self.control_queue = control_queue
        self.scan_interval = scan_interval

    class packet(object):
        def __init__(self, action, key = None):
            self.action = action
            self.key = key

class bot_info_T(object):
    def __init__(self, id = -1, password = '', server_type = 'post', server_auto = False, host = '', port = -1, access_token = None, platform_sdk = None, platform_platform = None, platform_model = None):
        self.id = id
        self.password = password
        self.platform = {}
        self.platform['sdk'] = platform_sdk
        self.platform['platform'] = platform_platform
        self.platform['model'] = platform_model
        self.hash = None
        self.post_info = self.post_info_T(
            server_auto = server_auto,
            server_type = server_type,
            host = host,
            port = port,
            access_token = access_token
        )
        self.debug_mode = False
        self.getHash()

    class post_info_T(object):
        def __init__(self, host = '', port = -1, access_token = None, server_type = 'post', server_auto = False):
            self.auto = server_auto
            self.type = server_type
            self.host = host
            self.port = port
            self.access_token = access_token

    def getHash(self):
        self.hash = getBotHash(
            bot_id = self.id,
            platform_sdk = self.platform['sdk'],
            platform_platform = self.platform['platform'],
            platform_model = self.platform['model']
        )

def getBotHash(bot_id = None, platform_sdk = None, platform_platform = None, platform_model = None):
    hash_tmp = hashlib.new('md5')
    hash_tmp.update(str(bot_id).encode(encoding='UTF-8'))
    hash_tmp.update(str(platform_sdk).encode(encoding='UTF-8'))
    hash_tmp.update(str(platform_platform).encode(encoding='UTF-8'))
    #hash_tmp.update(str(platform_model).encode(encoding='UTF-8'))
    return hash_tmp.hexdigest()

class Event(object):
    def __init__(self, sdk_event = None, log_func = None):
        self.bot_info = None
        self.platform = {}
        self.platform['sdk'] = None
        self.platform['platform'] = None
        self.platform['model'] = None
        self.data = None
        self.active = False
        self.blocked = False
        self.log_func = log_func
        self.base_info = {}
        self.base_info['time'] = None
        self.base_info['self_id'] = None
        self.base_info['type'] = None
        self.plugin_info = {}
        self.plugin_info['func_type'] = None
        self.plugin_info['message_mode_rx'] = OlivOS.infoAPI.OlivOS_message_mode_rx_default
        self.plugin_info['message_mode_tx'] = OlivOS.infoAPI.OlivOS_message_mode_tx_unity
        self.plugin_info['name'] = 'unity'
        self.plugin_info['namespace'] = 'unity'
        self.sdk_event = sdk_event
        self.sdk_event_type = type(self.sdk_event)
        self.get_Event_from_SDK()
        self.get_Event_on_Plugin()
        self.do_init_log()

    def get_Event_from_SDK(self):
        if self.sdk_event_type is OlivOS.onebotSDK.event:
            OlivOS.onebotSDK.get_Event_from_SDK(self)
        elif self.sdk_event_type is OlivOS.telegramSDK.event:
            OlivOS.telegramSDK.get_Event_from_SDK(self)

    def get_Event_on_Plugin(self):
        if self.plugin_info['func_type'] in [
            'private_message',
            'group_message'
        ]:
            if self.data.message_sdk.mode_rx == self.plugin_info['message_mode_tx']:
                self.data.message = self.data.message_sdk.data_raw
            else:
                self.data.message = self.data.message_sdk.get(self.plugin_info['message_mode_tx'])
            if self.data.raw_message_sdk.mode_rx == self.plugin_info['message_mode_tx']:
                self.data.raw_message = self.data.raw_message_sdk.data_raw
            else:
                self.data.raw_message = self.data.raw_message_sdk.get(self.plugin_info['message_mode_tx'])

    def do_init_log(self):
        if self.active:
            tmp_log_level = 0
            tmp_log_message = ''
            if self.plugin_info['func_type'] == 'private_message':
                tmp_log_level = 2
                tmp_log_message = 'User[' + self.data.sender['nickname'] + '](' + str(self.data.user_id) + ') : ' + self.data.message
            elif self.plugin_info['func_type'] == 'group_message':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User[' + self.data.sender['nickname'] + '](' + str(self.data.user_id) + ') : ' + self.data.message
            elif self.plugin_info['func_type'] == 'group_file_upload':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') : ' + self.data.file['name']
            elif self.plugin_info['func_type'] == 'group_admin':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') Action(' +  self.data.action + ')'
            elif self.plugin_info['func_type'] == 'group_member_decrease':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') <- Operator(' +  str(self.data.operator_id) + ') Action(' + self.data.action + ')'
            elif self.plugin_info['func_type'] == 'group_member_increase':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') <- Operator(' +  str(self.data.operator_id) + ') Action(' + self.data.action + ')'
            elif self.plugin_info['func_type'] == 'group_ban':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') <- Operator(' +  str(self.data.operator_id) + ') Duration(' + str(self.data.duration) + ') Action(' + self.data.action + ')'
            elif self.plugin_info['func_type'] == 'friend_add':
                tmp_log_level = 2
                tmp_log_message = 'User(' + str(self.data.user_id) + ')'
            elif self.plugin_info['func_type'] == 'group_message_recall':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') <- Operator(' +  str(self.data.operator_id) + ') Message_id(' + str(self.data.message_id) + ')'
            elif self.plugin_info['func_type'] == 'private_message_recall':
                tmp_log_level = 2
                tmp_log_message = 'User(' + str(self.data.user_id) + ') Message_id(' + str(self.data.message_id) + ')'
            elif self.plugin_info['func_type'] == 'poke':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') -> Target(' +  str(self.data.target_id) + ')'
            elif self.plugin_info['func_type'] == 'group_lucky_king':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') -> Target(' +  str(self.data.target_id) + ')'
            elif self.plugin_info['func_type'] == 'group_honor':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') Type(' + str(self.data.type) + ')'
            elif self.plugin_info['func_type'] == 'friend_add_request':
                tmp_log_level = 2
                tmp_log_message = 'User(' + str(self.data.user_id) + ') Flag(' + str(self.data.flag) + ') : ' + self.sdk_event.json['comment']
            elif self.plugin_info['func_type'] == 'group_add_request':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') Flag(' + str(self.data.flag) + ') : ' + self.sdk_event.json['comment']
            elif self.plugin_info['func_type'] == 'group_invite_request':
                tmp_log_level = 2
                tmp_log_message = 'Group(' + str(self.data.group_id) + ') User(' + str(self.data.user_id) + ') Flag(' + str(self.data.flag) + ') : ' + self.sdk_event.json['comment']
            elif self.plugin_info['func_type'] == 'lifecycle':
                tmp_log_level = 2
                tmp_log_message = 'Action(' + str(self.data.action) + ')'
            elif self.plugin_info['func_type'] == 'heartbeat':
                tmp_log_level = 1
                tmp_log_message = 'Interval(' + str(self.data.interval) + ')'
            self.log_func(tmp_log_level, tmp_log_message, [
                (self.platform['platform'], 'default'),
                (self.plugin_info['name'], 'default'),
                (self.plugin_info['func_type'], 'default')
            ])

    class private_message(object):
        def __init__(self, user_id, message, sub_type, flag_lazy = True):
            self.sub_type = sub_type
            self.message = message
            self.message_sdk = message
            self.message_id = None
            self.raw_message = None
            self.raw_message_sdk = None
            self.user_id = user_id
            self.font = None
            self.sender = {}
            if flag_lazy:
                self.sender['nickname'] = 'Nobody'

    class group_message(object):
        def __init__(self, group_id, user_id, message, sub_type, flag_lazy = True):
            self.sub_type = sub_type
            self.group_id = group_id
            self.message = message
            self.message_sdk = message
            self.message_id = None
            self.raw_message = None
            self.raw_message_sdk = None
            self.user_id = user_id
            self.font = None
            self.sender = {}
            if flag_lazy:
                self.sender['nickname'] = 'Nobody'

    class group_file_upload(object):
        def __init__(self, group_id, user_id, flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.file = {}
            if flag_lazy:
                self.file['id'] = 'Nofileid'
                self.file['name'] = 'Nofile'
                self.file['size'] = 0
                self.file['busid'] = -1

    class group_admin(object):
        def __init__(self, group_id, user_id, flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.action = 'unset'

    class group_member_decrease(object):
        def __init__(self, group_id, operator_id, user_id, action = 'leave', flag_lazy = True):
            self.group_id = group_id
            self.operator_id = operator_id
            self.user_id = user_id
            self.action = action

    class group_member_increase(object):
        def __init__(self, group_id, operator_id, user_id, action = 'approve', flag_lazy = True):
            self.group_id = group_id
            self.operator_id = operator_id
            self.user_id = user_id
            self.action = action

    class group_ban(object):
        def __init__(self, group_id, operator_id, user_id, duration, action = 'unban', flag_lazy = True):
            self.group_id = group_id
            self.operator_id = operator_id
            self.user_id = user_id
            self.duration = duration
            self.action = action

    class friend_add(object):
        def __init__(self, user_id, flag_lazy = True):
            self.user_id = user_id

    class group_message_recall(object):
        def __init__(self, group_id, operator_id, user_id, message_id, flag_lazy = True):
            self.group_id = group_id
            self.operator_id = operator_id
            self.user_id = user_id
            self.message_id = message_id

    class private_message_recall(object):
        def __init__(self, user_id, message_id, flag_lazy = True):
            self.user_id = user_id
            self.message_id = message_id

    class poke(object):
        def __init__(self, user_id, target_id, group_id = -1, flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.target_id = target_id

    class group_lucky_king(object):
        def __init__(self, group_id, user_id, target_id, flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.target_id = target_id

    class group_honor(object):
        def __init__(self, group_id, user_id, flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.type = None

    class friend_add_request(object):
        def __init__(self, user_id, comment = '', flag_lazy = True):
            self.user_id = user_id
            self.comment = comment
            self.flag = None

    class group_add_request(object):
        def __init__(self, group_id, user_id, comment = '', flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.comment = comment
            self.flag = None

    class group_invite_request(object):
        def __init__(self, group_id, user_id, comment = '', flag_lazy = True):
            self.group_id = group_id
            self.user_id = user_id
            self.comment = comment
            self.flag = None

    class lifecycle(object):
        def __init__(self, action = None, flag_lazy = True):
            self.action = action

    class heartbeat(object):
        def __init__(self, interval, flag_lazy = True):
            self.interval = interval


    def callbackLogger(func_name = None):
        def callbackLoggerDecorator(func):
            @wraps(func)
            def funcWarpped(*args, **kwargs):
                warppedRes = func(*args, **kwargs)
                flag_log = True
                event_obj = None
                callback_msg = 'done'
                if 'flag_log' in kwargs:
                    flag_log = kwargs['flag_log']
                if len(args) >= 1:
                    event_obj = args[0]
                if flag_log and event_obj != None:
                    if warppedRes == None:
                        callback_msg = 'done'
                    elif warppedRes.__class__.__base__ == dict:
                        if 'active' in warppedRes:
                            if warppedRes['active'] == True:
                                callback_msg = 'succeed'
                            else:
                                callback_msg = 'failed'
                        else:
                            callback_msg = 'done'
                    event_obj.log_func(2, callback_msg , [
                        (event_obj.platform['platform'], 'default'),
                        (event_obj.plugin_info['name'], 'default'),
                        (func_name, 'callback')
                    ])
                return warppedRes
            return funcWarpped
        return callbackLoggerDecorator


    #以下为统一事件动作调用方法实现，各接入sdk需完全支持

    def __set_block(self, enable, flag_log = True):
        self.blocked = enable
        if flag_log:
            self.log_func(2, str(enable) , [
                (self.platform['platform'], 'default'),
                (self.plugin_info['name'], 'default'),
                ('set_block', 'callback')
            ])

    def set_block(self, enable = True, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_block(enable, flag_log = True)

    def __reply(self, message, flag_log = True):
        flag_type = None
        if checkByListOrEqual(
            self.plugin_info['func_type'],
            [
                'private_message',
                'friend_add',
                'private_message_recall',
                'friend_add_request'
            ]
        ):
            self.__send('private', self.data.user_id, message, flag_log = False)
            flag_type = 'private'
        elif checkByListOrEqual(
            self.plugin_info['func_type'],
            [
                'group_message',
                'group_file_upload',
                'group_admin',
                'group_member_decrease',
                'group_member_increase',
                'group_ban',
                'group_message_recall',
                'group_lucky_king',
                'group_honor',
                'group_add_request',
                'group_invite_request'
                
            ]
        ):
            self.__send('group', self.data.group_id, message, flag_log = False)
            flag_type = 'group'
        elif checkByListOrEqual(
            self.plugin_info['func_type'],
            [
                'poke'
            ]
        ):
            if self.data.group_id == -1:
                self.__send('private', self.data.user_id, message, flag_log = False)
                flag_type = 'private'
            else:
                self.__send('group', self.data.group_id, message, flag_log = False)
                flag_type = 'group'

        if flag_log:
            if flag_type == 'private':
                self.log_func(2, 'User(' + str(self.data.user_id) + '): ' + message, [
                    (self.platform['platform'], 'default'),
                    (self.plugin_info['name'], 'default'),
                    ('reply', 'callback')
                ])
            elif flag_type == 'group':
                self.log_func(2, 'Group(' + str(self.data.group_id) + '): ' + message, [
                    (self.platform['platform'], 'default'),
                    (self.plugin_info['name'], 'default'),
                    ('reply', 'callback')
                ])

    def reply(self, message, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__reply(message, flag_log = True)


    def __send(self, send_type, target_id, message, flag_log = True):
        flag_type = send_type
        if self.platform['sdk'] == 'onebot':
            if flag_type == 'private':
                OlivOS.onebotSDK.event_action.send_private_msg(self, target_id, message)
            elif flag_type == 'group':
                OlivOS.onebotSDK.event_action.send_group_msg(self, target_id, message)
        elif self.platform['sdk'] == 'telegram_poll':
            OlivOS.telegramSDK.event_action.send_msg(self, target_id, message)

        if flag_log:
            if flag_type == 'private':
                self.log_func(2, 'User(' + str(target_id) + '): ' + message, [
                    (self.platform['platform'], 'default'),
                    (self.plugin_info['name'], 'default'),
                    ('send', 'callback')
                ])
            elif flag_type == 'group':
                self.log_func(2, 'Group(' + str(target_id) + '): ' + message, [
                    (self.platform['platform'], 'default'),
                    (self.plugin_info['name'], 'default'),
                    ('send', 'callback')
                ])

    def send(self, send_type, target_id, message, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__send(send_type, target_id, message, flag_log = True)

    @callbackLogger('delete_msg')
    def __delete_msg(self, message_id, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.delete_msg(self, message_id)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def delete_msg(self, message_id, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__delete_msg(message_id, flag_log = True)

    @callbackLogger('get_msg')
    def __get_msg(self, message_id, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_msg(self, message_id)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_msg(self, message_id, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_msg(message_id, flag_log = True)
        return res_data


    @callbackLogger('send_like')
    def __send_like(self, user_id, times, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.send_like(self, user_id, times)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def send_like(self, user_id, times = 1, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__send_like(user_id, times, flag_log = True)


    @callbackLogger('set_group_kick')
    def __set_group_kick(self, group_id, user_id, rehect_add_request, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_kick(self, group_id, user_id, rehect_add_request)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_kick(self, group_id, user_id, rehect_add_request = False, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_kick(group_id, user_id, rehect_add_request, flag_log = True)


    @callbackLogger('set_group_ban')
    def __set_group_ban(self, group_id, user_id, duration, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_ban(self, group_id, user_id, duration)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_ban(self, group_id, user_id, duration = 1800, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_ban(group_id, user_id, duration, flag_log = True)


    @callbackLogger('set_group_anonymous_ban')
    def __set_group_anonymous_ban(self, group_id, anonymous, anonymous_flag, duration, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_anonymous_ban(self, group_id, anonymous, anonymous_flag, duration)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_anonymous_ban(self, group_id, anonymous, anonymous_flag, duration = 1800, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_anonymous_ban(group_id, anonymous, anonymous_flag, duration, flag_log = True)


    @callbackLogger('set_group_whole_ban')
    def __set_group_whole_ban(self, group_id, enable, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_whole_ban(self, group_id, enable)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_whole_ban(self, group_id, enable, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_whole_ban(group_id, enable, flag_log = True)


    @callbackLogger('set_group_admin')
    def __set_group_admin(self, group_id, user_id, enable, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_admin(self, group_id, user_id, enable)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_admin(self, group_id, user_id, enable, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_admin(group_id, user_id, enable, flag_log = True)


    @callbackLogger('set_group_anonymous')
    def __set_group_anonymous(self, group_id, enable, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_anonymous(self, group_id, enable)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_anonymous(self, group_id, enable, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_anonymous(group_id, enable, flag_log = True)


    @callbackLogger('set_group_card')
    def __set_group_card(self, group_id, user_id, card, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_card(self, group_id, user_id, card)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_card(self, group_id, user_id, card, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_card(group_id, user_id, card, flag_log = True)


    @callbackLogger('set_group_name')
    def __set_group_name(self, group_id, group_name, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_name(self, group_id, group_name)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_name(self, group_id, group_name, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_name(group_id, group_name, flag_log = True)


    @callbackLogger('set_group_leave')
    def __set_group_leave(self, group_id, is_dismiss, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_leave(self, group_id, is_dismiss)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_leave(self, group_id, is_dismiss = False, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_leave(group_id, is_dismiss, flag_log = True)


    @callbackLogger('set_group_special_title')
    def __set_group_special_title(self, group_id, user_id, special_title, duration, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_special_title(self, group_id, user_id, special_title, duration)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_special_title(self, group_id, user_id, special_title, duration, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_special_title(group_id, user_id, special_title, duration, flag_log = True)


    @callbackLogger('set_friend_add_request')
    def __set_friend_add_request(self, flag, approve, remark, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_friend_add_request(self, flag, approve, remark)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_friend_add_request(self, flag, approve, remark, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_friend_add_request(flag, approve, remark, flag_log = True)


    @callbackLogger('set_group_add_request')
    def __set_group_add_request(self, flag, sub_type, approve, reason, flag_log = True):
        if self.platform['sdk'] == 'onebot':
            OlivOS.onebotSDK.event_action.set_group_add_request(self, flag, sub_type, approve, reason)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

    def set_group_add_request(self, flag, sub_type, approve, reason, flag_log = True, remote = False):
        if remote:
            pass
        else:
            self.__set_group_add_request(flag, sub_type, approve, reason, flag_log = True)


    def __get_login_info(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_login_info(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass

        if res_data == None:
            return None

        if flag_log:
            if checkDictByListAnd(
                res_data, [
                    ['active'],
                    ['data', 'name'],
                    ['data', 'id']
                ]
            ):
                if res_data['active'] == True:
                    self.log_func(2, 'name(' + res_data['data']['name'] + ') id(' + str(res_data['data']['id']) + ')' , [
                        (self.platform['platform'], 'default'),
                        (self.plugin_info['name'], 'default'),
                        ('get_login_info', 'callback')
                    ])
                else:
                    self.log_func(2, 'failed' , [
                        (self.platform['platform'], 'default'),
                        (self.plugin_info['name'], 'default'),
                        ('get_login_info', 'callback')
                    ])
        return res_data

    def get_login_info(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_login_info(flag_log = True)
        return res_data


    @callbackLogger('get_stranger_info')
    def __get_stranger_info(self, user_id, no_cache, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_stranger_info(self, user_id, no_cache)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_stranger_info(self, user_id, no_cache = False, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_stranger_info(user_id, no_cache, flag_log = True)
        return res_data


    @callbackLogger('get_friend_list')
    def __get_friend_list(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_friend_list(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_friend_list(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_friend_list(flag_log = True)
        return res_data


    @callbackLogger('get_group_info')
    def __get_group_info(self, group_id, no_cache, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_group_info(self, group_id, no_cache)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_group_info(self, group_id, no_cache = False, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_group_info(group_id, no_cache, flag_log = True)
        return res_data


    @callbackLogger('get_group_list')
    def __get_group_list(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_group_list(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_group_list(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_group_list(flag_log = True)
        return res_data


    @callbackLogger('get_group_member_info')
    def __get_group_member_info(self, group_id, user_id, no_cache, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_group_member_info(self, group_id, user_id, no_cache)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_group_member_info(self, group_id, user_id, no_cache = False, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_group_member_info(group_id, user_id, no_cache, flag_log = True)
        return res_data


    @callbackLogger('get_group_member_list')
    def __get_group_member_list(self, group_id, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_group_member_list(self, group_id)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_group_member_list(self, group_id, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_group_member_list(group_id, flag_log = True)
        return res_data


    @callbackLogger('can_send_image')
    def __can_send_image(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.can_send_image(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def can_send_image(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__can_send_image(flag_log = True)
        return res_data


    @callbackLogger('can_send_record')
    def __can_send_record(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.can_send_record(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def can_send_record(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__can_send_record(flag_log = True)
        return res_data


    @callbackLogger('get_status')
    def __get_status(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_status(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_status(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_status(flag_log = True)
        return res_data


    @callbackLogger('get_version_info')
    def __get_version_info(self, flag_log = True):
        res_data = None
        if self.platform['sdk'] == 'onebot':
            res_data = OlivOS.onebotSDK.event_action.get_version_info(self)
        elif self.platform['sdk'] == 'telegram_poll':
            pass
        return res_data

    def get_version_info(self, flag_log = True, remote = False):
        res_data = None
        if remote:
            pass
        else:
            res_data = self.__get_version_info(flag_log = True)
        return res_data


class api_result_data_template(object):
    class get_msg(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'message_id': None,
                    'id': -1,
                    'sender': {
                        'id': -1,
                        'name': None
                    },
                    'time': -1,
                    'message': None,
                    'raw_message': None
                }
            )

    class get_login_info(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'name': None,
                    'id': -1
                }
            )

    class get_user_info_strip(dict):
        def __init__(self):
            self.update(
                {
                    'name': None,
                    'id': -1
                }
            )

    class get_stranger_info(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(api_result_data_template.get_user_info_strip())

    class get_friend_list(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = []

    class get_group_info_strip(dict):
        def __init__(self):
            self.update(
                {
                    'name': None,
                    'id': -1,
                    'memo': None,
                    'max_member_count': 0
                }
            )

    class get_group_info(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(api_result_data_template.get_group_info_strip())

    class get_group_list(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = []

    class get_group_member_info_strip(dict):
        def __init__(self):
            self.update(
                {
                    'name': None,
                    'id': -1,
                    'user_id': -1,
                    'group_id': -1,
                    'times': {
                        'join_time': 0,
                        'last_sent_time': 0,
                        'shut_up_timestamp': 0
                    },
                    'role': None,
                    'card': None,
                    'title': None
                }
            )

    class get_group_member_info(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(api_result_data_template.get_group_member_info_strip())

    class get_group_member_list(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = []

    class can_send_image(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'yes': False
                }
            )

        def yes(self):
            if self['data']['yes'] == True:
                return True
            return False

    class can_send_record(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'yes': False
                }
            )

        def yes(self):
            if self['data']['yes'] == True:
                return True
            return False

    class get_status(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'online': False,
                    'status': {
                        'packet_received': 0,
                        'packet_sent': 0,
                        'packet_lost': 0,
                        'message_received': 0,
                        'message_sent': 0,
                        'disconnect_times': 0,
                        'lost_times': 0,
                        'last_message_time': 0
                    }
                }
            )

    class get_version_info(dict):
        def __init__(self):
            self['active'] = False
            self['data'] = {}
            self['data'].update(
                {
                    'name': None,
                    'version_full': None,
                    'version': None,
                    'path': None,
                    'os': None
                }
            )

class Proc_templet(object):
    def __init__(self, Proc_name = 'native_plugin', Proc_type = 'default', scan_interval = 0.001, dead_interval = 1, rx_queue = None, tx_queue = None, control_queue = None, logger_proc = None):
        self.deamon = True
        self.Proc = None
        self.Proc_name = Proc_name
        self.Proc_type = Proc_type
        self.Proc_info = self.Proc_info_T(
            rx_queue = rx_queue,
            tx_queue = tx_queue,
            control_queue = control_queue,
            logger_proc = logger_proc,
            scan_interval = scan_interval,
            dead_interval = dead_interval
        )
        self.Proc_config = {}
        self.Proc_data = {}

    class Proc_info_T(object):
        def __init__(self, rx_queue, tx_queue, control_queue, logger_proc, scan_interval = 0.001, dead_interval = 1):
            self.rx_queue = rx_queue
            self.tx_queue = tx_queue
            self.control_queue = control_queue
            self.logger_proc = logger_proc
            self.scan_interval = scan_interval
            self.dead_interval = dead_interval

    def run(self):
        pass

    def start(self):
        proc_this = multiprocessing.Process(name = self.Proc_name, target = self.run, args = ())
        proc_this.daemon = self.deamon
        proc_this.start()
        self.Proc = proc_this
        return self.Proc

    def log(self, log_level, log_message, log_segment = []):
        if self.Proc_info.logger_proc != None:
            self.Proc_info.logger_proc.log(log_level, log_message, log_segment)

#兼容Win平台的进程生成方法
def Proc_start(proc_this):
    proc_proc_this = multiprocessing.Process(name = proc_this.Proc_name, target = proc_this.run, args = ())
    proc_proc_this.daemon = proc_this.deamon
    #multiprocessing.Process无法进行弱引用序列化烘培，故无法在Win平台下实现自动更新进程引用
    #proc_this.Proc = proc_proc_this
    proc_proc_this.start()
    return proc_proc_this

class Proc_info_T(object):
    def __init__(self, rx_queue, tx_queue, logger_proc, scan_interval = 0.001):
        self.rx_queue = rx_queue
        self.tx_queue = tx_queue
        self.logger_proc = logger_proc
        self.scan_interval = scan_interval

class Message_templet(object):
    def __init__(self, mode_rx, data_raw):
        self.active = True
        self.mode_rx = mode_rx
        self.data = []
        self.data_raw = data_raw
        try:
            self.init_data()
        except:
            self.active = False
            self.data = []

    def __str__(self):
        tmp_res = self.__dict__.copy()
        tmp_res_data = []
        for data_this in tmp_res['data']:
            tmp_res_data.append(data_this.__dict__)
        tmp_res['data'] = tmp_res_data
        return str(tmp_res)

    def append(self, para_append):
        self.data.append(para_append)

    def match_str(self, src_str, match_str_src):
        if len(src_str) >= len(match_str_src):
            if src_str[:len(match_str_src)] == match_str_src:
                return True
        return False

    def get_from_dict(self, src_dict, key_list, default_val = None):
        tmp_src_dict = src_dict
        for key_list_this in key_list:
            if key_list_this in tmp_src_dict:
                tmp_src_dict = tmp_src_dict[key_list_this]
            else:
                return default_val
        return tmp_src_dict

    def get(self, get_type):
        res = None
        if not self.active:
            res = str(self)
        elif get_type == 'olivos_para':
            res = self
        elif get_type == 'olivos_string':
            res = ''
            for data_this in self.data:
                res += data_this.OP()
        elif get_type == 'old_string':
            res = ''
            for data_this in self.data:
                res += data_this.CQ()
        else:
            res = str(self)
        return res

    def init_data(self):
        if self.mode_rx == 'olivos_para':
            self.init_from_olivos_para()
        elif self.mode_rx == 'olivos_para':
            self.init_from_code_string('OP')
        elif self.mode_rx == 'old_string':
            self.init_from_code_string('CQ')

    def init_from_olivos_para(self):
        self.data = self.data_raw

    def init_from_code_string(self, code_key):
        tmp_data_raw = self.data_raw
        tmp_data = []
        it_data = range(0, len(tmp_data_raw) + 1)
        it_data_base = 0
        tmp_data_type = 'string'
        for it_data_this in it_data:
            if tmp_data_type == 'string' and self.match_str(tmp_data_raw[it_data_this:], '[' + code_key + ':'):
                tmp_para_this = None
                if it_data_this > it_data_base:
                    tmp_data_raw_this = tmp_data_raw[it_data_base:it_data_this]
                    tmp_para_this = PARA.text(tmp_data_raw_this)
                    tmp_data.append(tmp_para_this)
                it_data_base = it_data_this
                tmp_data_type = 'code'
            elif tmp_data_type == 'code' and self.match_str(tmp_data_raw[it_data_this:], ']'):
                tmp_para_this = None
                if it_data_this > it_data_base:
                    tmp_data_raw_this_bak = tmp_data_raw[it_data_base:it_data_this + 1]
                    tmp_data_raw_this = tmp_data_raw_this_bak
                    tmp_data_raw_this = tmp_data_raw_this[len('[' + code_key + ':'):]
                    tmp_data_raw_this = tmp_data_raw_this[:-len(']')]
                    tmp_data_raw_this_list = tmp_data_raw_this.split(',')
                    tmp_data_type_key = tmp_data_raw_this_list[0]
                    tmp_code_data_list = tmp_data_raw_this_list[1:]
                    tmp_code_data_dict = {}
                    for tmp_code_data_list_this in tmp_code_data_list:
                        tmp_code_data_list_this_list = tmp_code_data_list_this.split('=')
                        tmp_code_data_list_this_key = tmp_code_data_list_this_list[0]
                        tmp_code_data_list_this_val = ''
                        flag_tmp_code_data_list_this_val_begin = True
                        for tmp_code_data_list_this_val_this in tmp_code_data_list_this_list[1:]:
                            if not flag_tmp_code_data_list_this_val_begin:
                                tmp_code_data_list_this_val += '='
                            else:
                                flag_tmp_code_data_list_this_val_begin = False
                            tmp_code_data_list_this_val += tmp_code_data_list_this_val_this
                        tmp_code_data_dict[tmp_code_data_list_this_key] = tmp_code_data_list_this_val
                    if tmp_data_type_key == 'face':
                        tmp_para_this = PARA.face(
                            id = str(self.get_from_dict(tmp_code_data_dict, ['id']))
                        )
                    elif tmp_data_type_key == 'at':
                        if code_key == 'CQ':
                            tmp_code_data_dict['id'] = str(self.get_from_dict(tmp_code_data_dict, ['qq'], -1))
                        tmp_para_this = PARA.at(
                            id = int(self.get_from_dict(tmp_code_data_dict, ['id'], -1))
                        )
                    elif tmp_data_type_key == 'reply':
                        tmp_para_this = PARA.reply(
                            id = str(self.get_from_dict(tmp_code_data_dict, ['id'], 0))
                        )
                    elif tmp_data_type_key == 'image':
                        tmp_para_this = PARA.image(
                            file = str(self.get_from_dict(tmp_code_data_dict, ['file'])),
                            type = str(self.get_from_dict(tmp_code_data_dict, ['type'], 'show')),
                            url = str(self.get_from_dict(tmp_code_data_dict, ['url']))
                        )
                    elif tmp_data_type_key == 'record':
                        tmp_para_this = PARA.record(
                            file = str(self.get_from_dict(tmp_code_data_dict, ['file'])),
                            url = str(self.get_from_dict(tmp_code_data_dict, ['url']))
                        )
                    elif tmp_data_type_key == 'video':
                        tmp_para_this = PARA.video(
                            file = str(self.get_from_dict(tmp_code_data_dict, ['file'])),
                            url = str(self.get_from_dict(tmp_code_data_dict, ['url']))
                        )
                    elif tmp_data_type_key == 'rps':
                        tmp_para_this = PARA.rps()
                    elif tmp_data_type_key == 'dice':
                        tmp_para_this = PARA.dice()
                    elif tmp_data_type_key == 'shake':
                        tmp_para_this = PARA.shake()
                    elif tmp_data_type_key == 'poke':
                        tmp_para_this = PARA.poke(
                            id = int(self.get_from_dict(tmp_code_data_dict, ['id'], -1))
                        )
                    elif tmp_data_type_key == 'anonymous':
                        tmp_para_this = PARA.anonymous()
                    elif tmp_data_type_key == 'share':
                        tmp_para_this = PARA.share(
                            url = str(self.get_from_dict(tmp_code_data_dict, ['url'], '')),
                            title = str(self.get_from_dict(tmp_code_data_dict, ['title'], '')),
                            content = str(self.get_from_dict(tmp_code_data_dict, ['content'], '')),
                            image = str(self.get_from_dict(tmp_code_data_dict, ['image'], ''))
                        )
                    elif tmp_data_type_key == 'location':
                        tmp_para_this = PARA.location(
                            lat = str(self.get_from_dict(tmp_code_data_dict, ['lat'], '')),
                            lon = str(self.get_from_dict(tmp_code_data_dict, ['lon'], '')),
                            title = str(self.get_from_dict(tmp_code_data_dict, ['title'], '')),
                            content = str(self.get_from_dict(tmp_code_data_dict, ['content'], ''))
                        )
                    elif tmp_data_type_key == 'music':
                        tmp_para_this = PARA.music(
                            type = str(self.get_from_dict(tmp_code_data_dict, ['type'], '')),
                            id = str(self.get_from_dict(tmp_code_data_dict, ['id'], '')),
                            url = str(self.get_from_dict(tmp_code_data_dict, ['url'], '')),
                            audio = str(self.get_from_dict(tmp_code_data_dict, ['audio'], '')),
                            title = str(self.get_from_dict(tmp_code_data_dict, ['title'], '')),
                            content = str(self.get_from_dict(tmp_code_data_dict, ['content'], '')),
                            image = str(self.get_from_dict(tmp_code_data_dict, ['image'], ''))
                        )
                    elif tmp_data_type_key == 'forward':
                        tmp_para_this = PARA.forward(
                            id = int(self.get_from_dict(tmp_code_data_dict, ['id'], -1))
                        )
                    elif tmp_data_type_key == 'xml':
                        tmp_para_this = PARA.xml(
                            data = str(self.get_from_dict(tmp_code_data_dict, ['data'], ''))
                        )
                    elif tmp_data_type_key == 'json':
                        tmp_para_this = PARA.json(
                            data = str(self.get_from_dict(tmp_code_data_dict, ['data'], ''))
                        )
                    else:
                        tmp_para_this = PARA.text(tmp_data_raw_this_bak)
                    tmp_data.append(tmp_para_this)
                it_data_base = it_data_this + 1
                tmp_data_type = 'string'
            elif it_data_this >= len(tmp_data_raw):
                tmp_para_this = None
                if it_data_this > it_data_base:
                    tmp_data_raw_this = tmp_data_raw[it_data_base:it_data_this + 1]
                    tmp_para_this = PARA.text(tmp_data_raw_this)
                    tmp_data.append(tmp_para_this)
                it_data_base = it_data_this
        self.data = tmp_data

class PARA_templet(object):
    def __init__(self, type = None, data = None):
        self.type = type
        self.data = data

    def CQ(self):
        return self.get_string_by_key('CQ')

    def OP(self):
        return self.get_string_by_key('OP')

    def get_string_by_key(self, code_key):
        code_tmp = '[' + code_key + ':' + self.type
        if self.data != None:
            for key_this in self.data:
                if self.data[key_this] != None:
                    code_tmp += ',' + key_this + '=' + str(self.data[key_this])
        code_tmp += ']'
        return code_tmp

    def PARA(self):
        PARA_tmp = self.cut()
        if self.data == None:
            PARA_tmp.data = dict()
        return json.dumps(obj = PARA_tmp.__dict__)

    def copy(self):
        copy_tmp = PARA_templet(self.type, self.data.copy())
        return copy_tmp

    def cut(self):
        copy_tmp = self.copy()
        if copy_tmp.data != None:
            for key_this in self.data:
                if copy_tmp.data[key_this] == None:
                    del copy_tmp.data[key_this]
                else:
                    copy_tmp.data[key_this] = str(copy_tmp.data[key_this])
        return copy_tmp

    def __str__(self):
        return str(self.__dict__)

class PARA(object):
    class text(PARA_templet):
        def __init__(self, text = ''):
            PARA_templet.__init__(self, 'text', self.data_T(text))

        class data_T(dict):
            def __init__(self, text = ''):
                self['text'] = text

        def get_string_by_key(self, code_key):
            if self.data != None:
                if type(self.data['text']) is str:
                    return self.data['text']
                else:
                    return str(self.data['text'])
            else:
                return ''

    class face(PARA_templet):
        def __init__(self, id):
            PARA_templet.__init__(self, 'face', self.data_T(id))

        class data_T(dict):
            def __init__(self, id):
                self['id'] = id

    class image(PARA_templet):
        def __init__(self, file, type = None, url = None, cache = None, proxy = None, timeout = None):
            PARA_templet.__init__(self, 'image', self.data_T(file, type, url, cache, proxy, timeout))

        class data_T(dict):
            def __init__(self, file, type, url, cache, proxy, timeout):
                self['file'] = file
                self['type'] = type
                self['url'] = url
                self['cache'] = cache
                self['proxy'] = proxy
                self['timeout'] = timeout

    class record(PARA_templet):
        def __init__(self, file, magic = None, url = None, cache = None, proxy = None, timeout = None):
            PARA_templet.__init__(self, 'record', self.data_T(file, magic, url, cache, proxy, timeout))

        class data_T(dict):
            def __init__(self, file, magic, url, cache, proxy, timeout):
                self['file'] = file
                self['magic'] = magic
                self['url'] = url
                self['cache'] = cache
                self['proxy'] = proxy
                self['timeout'] = timeout

    class video(PARA_templet):
        def __init__(self, file, url = None, cache = None, proxy = None, timeout = None):
            PARA_templet.__init__(self, 'record', self.data_T(file, url, cache, proxy, timeout))

        class data_T(dict):
            def __init__(self, file, url, cache, proxy, timeout):
                self['file'] = file
                self['url'] = url
                self['cache'] = cache
                self['proxy'] = proxy
                self['timeout'] = timeout

    class at(PARA_templet):
        def __init__(self, id):
            PARA_templet.__init__(self, 'at', self.data_T(id))

        class data_T(dict):
            def __init__(self, id):
                self['id'] = id

        def get_string_by_key(self, code_key):
            code_tmp = '[' + code_key + ':' + self.type
            if self.data != None:
                for key_this in self.data:
                    if self.data[key_this] != None:
                        if code_key == 'CQ' and key_this == 'id':
                            code_tmp += ',qq=' + str(self.data[key_this])
                        else:
                            code_tmp += ',' + key_this + '=' + str(self.data[key_this])
            code_tmp += ']'
            return code_tmp

    class rps(PARA_templet):
        def __init__(self):
            PARA_templet.__init__(self, 'rps', None)

    class dice(PARA_templet):
        def __init__(self):
            PARA_templet.__init__(self, 'dice', None)

    class shake(PARA_templet):
        def __init__(self):
            PARA_templet.__init__(self, 'shake', None)

    class poke(PARA_templet):
        def __init__(self, type, id, name = None):
            PARA_templet.__init__(self, 'poke', self.data_T(type, id, name))

        class data_T(dict):
            def __init__(self, type, id, name):
                self['type'] = type
                self['id'] = id
                self['name'] = name

    class anonymous(PARA_templet):
        def __init__(self):
            PARA_templet.__init__(self, 'anonymous', None)

    class share(PARA_templet):
        def __init__(self, url, title, content = None, image = None):
            PARA_templet.__init__(self, 'share', self.data_T(url, title, content, image))

        class data_T(dict):
            def __init__(self, url, title, content, image):
                self['url'] = url
                self['title'] = title
                self['content'] = content
                self['image'] = image

    class contact(PARA_templet):
        def __init__(self, type, id):
            PARA_templet.__init__(self, 'contact', self.data_T(type, id))

        class data_T(dict):
            def __init__(self, type, id):
                self['type'] = type
                self['id'] = id

    class location(PARA_templet):
        def __init__(self, lat, lon, title = None, content = None):
            PARA_templet.__init__(self, 'location', self.data_T(lat, lon, title, content))

        class data_T(dict):
            def __init__(self, lat, lon, title, content):
                self['lat'] = lat
                self['lon'] = lon
                self['title'] = title
                self['content'] = content

    class music(PARA_templet):
        def __init__(self, type, id = None, url = None, audio = None, title = None, content = None, image = None):
            PARA_templet.__init__(self, 'music', self.data_T(type, id, url, audio, title, content, image))

        class data_T(dict):
            def __init__(self, type, id, url, audio, title, content, image):
                self['type'] = type
                self['id'] = id
                self['url'] = url
                self['audio'] = audio
                self['title'] = title
                self['content'] = content
                self['image'] = image

    class reply(PARA_templet):
        def __init__(self, id):
            PARA_templet.__init__(self, 'reply', self.data_T(id))

        class data_T(dict):
            def __init__(self, id):
                self['id'] = id

    class forward(PARA_templet):
        def __init__(self, id):
            PARA_templet.__init__(self, 'forward', self.data_T(id))

        class data_T(dict):
            def __init__(self, id):
                self['id'] = id

    class node(PARA_templet):
        def __init__(self, id = None, user_id = None, nickname = None, content = None):
            PARA_templet.__init__(self, 'node', self.data_T(id, user_id, nickname, content))

        class data_T(dict):
            def __init__(self, id, user_id, nickname, content):
                self['id'] = id
                self['user_id'] = user_id
                self['nickname'] = nickname
                self['content'] = content

    class xml(PARA_templet):
        def __init__(self, data, resid = None):
            PARA_templet.__init__(self, 'xml', self.data_T(data, resid))

        class data_T(dict):
            def __init__(self, data, resid):
                self['data'] = data
                self['resid'] = resid

    class json(PARA_templet):
        def __init__(self, data, resid = None):
            PARA_templet.__init__(self, 'json', self.data_T(data, resid))

        class data_T(dict):
            def __init__(self, data, resid):
                self['data'] = data
                self['resid'] = resid

def checkByListAnd(check_list):
    flag_res = True
    for check_list_this in check_list:
        if not check_list_this:
            flag_res = False
            return flag_res
    return flag_res

def checkByListOr(check_list):
    flag_res = False
    for check_list_this in check_list:
        if check_list_this:
            flag_res = True
            return flag_res
    return flag_res

def checkByListAndEqual(checked_obj, check_list):
    flag_res = True
    for check_list_this in check_list:
        if checked_obj != check_list_this:
            flag_res = False
            return flag_res
    return flag_res

def checkByListOrEqual(checked_obj, check_list):
    flag_res = False
    for check_list_this in check_list:
        if checked_obj == check_list_this:
            flag_res = True
            return flag_res
    return flag_res

def checkDictByListAnd(checked_obj, check_list):
    flag_res = True
    for check_list_this in check_list:
        tmp_checked_obj = checked_obj
        for check_list_this_this in check_list_this:
            if check_list_this_this in tmp_checked_obj:
                tmp_checked_obj = tmp_checked_obj[check_list_this_this]
            else:
                flag_res = False
                return flag_res
    return flag_res
