'''
Wrapper module for access to, and modification of, STEEM blockchain data.
Optimized by extensive use of generator functions and other means.
'''

import time
import re
import json
from steem import *

# begin SteemDataParser()
class SteemDataParser():
    def __init__(self, **kwargs):
        hash = kwargs

        try:
            nodes = hash['nodes']
            del( hash['nodes'] )
        except: nodes = None

        try:
            no_broadcast = hash['no_broadcast']
            del( hash['no_broadcast'] )
        except: no_broadcast = False

        self.__steem = Steem(nodes=nodes, \
                             no_broadcast=no_broadcast, **hash)


    def get_steem(self): return self.__steem
    
    def get_steemd(self): return self.__steem.steemd

    def get_commit(self): return self.__steem.commit

    def get_all_accounts(self, **kwargs):
        first_req_flag = True
        sel_arr = []
        start_uname = ''
        batch_size = 100
        el = None

        try:
            batch_size = kwargs['batch_size']
        except: pass
        
        while True:
            sel_arr = self.get_steemd().\
                      lookup_accounts(start_uname, batch_size)

            if not first_req_flag:
                del( sel_arr[0] )
            else: first_req_flag = False

            start_uname = sel_arr[ len(sel_arr) - 1 ]

            for el in sel_arr:
                yield el

            if len(sel_arr) < batch_size - 1: break

    def get_account_history(self, **kwargs):
        account = kwargs['account']

        try: limit = kwargs['limit']
        except: limit = 100

        completion_flag = False
        first_loop = True
        last_entry = 0
        sel_arr = []
        index_from = limit
        
        while True:
            sel_arr = self.get_steemd().\
                      get_account_history(account = account, \
                                          index_from = index_from, \
                                          limit = limit)

            if not first_loop:
                if sel_arr[len(sel_arr) - 1][0] == \
                   last_entry: completion_flag = True
            else: first_loop = False

            if ( len( sel_arr ) == 0 ): completion_flag = True
            else: last_entry = sel_arr[len(sel_arr) - 1][0]
            
            for el in sel_arr: yield BlogHistoryEntry(entry = el)

            if completion_flag: break

            index_from += limit

    
# end SteemDataParser()

# begin BlogAccount():
'''
BlogAccount(account = <account_name>)
'''
class BlogAccount():
    def __init__(self, **kwargs):
        self.__hash = kwargs

        try:
            sdp = self.__hash['steem_data_parser']
        except:
            sdp = SteemDataParser()
            self.__hash['steem_data_parser'] = sdp

        self.__hash['exists'] = \
                                sdp.get_steemd().\
                                get_account(account= self.__hash['account']) is not None

    def get_hash(self): return self.__hash
    
# end BlogAccount():

# begin BlogEntry()
'''
BlogEntry(account = <account_name>, author = <author>, permlink = <permlink> )
BlogEntry(account = <account_name>, url = <url> )
BlogEntry(url = <url> )
'''
class BlogEntry():
    def __init__(self, **kwargs):
        self.__hash = kwargs


        if 'url' in set(self.__hash.keys()) and \
           self.__hash['url'].startswith('https://steemit.com/'):
            url_str = self.__hash['url'].split(' ')[0]
            url_parts = url_str.split('/')[3:]
            self.__hash['permlink'] = url_parts[ len(url_parts) - 1 ]

            for el in url_parts:
                if el[0] == '@':
                    self.__hash['author'] = el[1:]
                    break
                
            if 'account' not in set(self.__hash.keys()) and \
               'author' in set(self.__hash.keys()):
                self.__hash['account'] = self.__hash['author']
            
        try:
            sdp = self.__hash['steem_data_parser']
        except:
            sdp = SteemDataParser()
            self.__hash['steem_data_parser'] = sdp

        self.__hash['exists'] = \
                                sdp.get_steemd().\
                                get_account(account= self.__hash['account']) is not None

        if not self.__hash['exists']: return

        self.__hash['exists'] = \
                                sdp.get_steemd().\
                                get_account(account= self.__hash['author']) is not None

        if not self.__hash['exists']: return

        self.__hash['exists'] = False

        for el in sdp.get_account_history(account = self.__hash['author']):
            if el.get_entry_type_hash()['type'] != 'comment': continue
            if el.get_hash()['entry'][1]['op'][1]['author'] != self.__hash['author']: continue
            if el.get_hash()['entry'][1]['op'][1]['permlink'] != self.__hash['permlink']: continue
            self.__hash['exists'] = True
            break
        
        if self.__hash['account'] == self.__hash['author']:
            self.__hash['entry_type'] = 'native'
        else:
            self.__hash['entry_type'] = 'reblogged'
        

    def get_hash(self): return self.__hash

    def exists_on_blockchain(self): return self.__hash['exists']

    def get_votes(self):
        sdp = self.__hash['steem_data_parser']
        
        for el in sdp.get_account_history(account = self.__hash['author']):
            if el.get_entry_type_hash()['type'] != 'vote': continue
            if el.get_hash()['entry'][1]['op'][1]['author'] != self.__hash['author']: continue
            if el.get_hash()['entry'][1]['op'][1]['permlink'] != self.__hash['permlink']: continue
            yield el
            
# end BlogEntry()

# begin BlogHistoryEntry()
'''
BlogHistoryEntry(entry=<entry>)
'''
class BlogHistoryEntry():
    def __init__(self, **kwargs):
        self.__hash = kwargs

    def get_hash(self): return self.__hash

    def get_entry(self): return self.__hash['entry']

    def get_entry_type_hash(self):
        hash = {}
        hash['type'] = self.__hash['entry'][1]['op'][0]

        if hash['type'] == 'custom_json':
            hash['subtype1'] = json.loads( self.__hash['entry'][1]['op'][1]['json'] )[0]

        return hash

    def get_timestamp(self): return self.__hash['entry'][1]['timestamp']

    def get_timestamp_utc(self):
        return time.mktime( time.strptime( self.get_timestamp() ) )

    def get_entry_id(self): return self.__hash['entry'][0]

    def get_trx_id(self): return self.__hash['entry'][1]['trx_id']

    def get_block(self): return self.__hash['entry'][1]['block']

    def get_author(self):
        try:
            return self.__hash['entry'][1]['op'][1]['author']
        except:
            return None

    def get_voter(self):
        try:
            return self.__hash['entry'][1]['op'][1]['voter']
        except:
            return None

    def get_permlink(self):
        try:
            return self.__hash['entry'][1]['op'][1]['permlink']
        except:
            return None

    def get_transfer_sender(self):
        try:
            return self.__hash['entry'][1]['op'][1]['from']
        except:
            return None

    def get_transfer_recipient(self):
        try:
            return self.__hash['entry'][1]['op'][1]['to']
        except:
            return None        

    def get_transfer_amount(self):
        try:
            return self.__hash['entry'][1]['op'][1]['amount']
        except:
            return None

    def get_transfer_memo(self):
        try:
            return self.__hash['entry'][1]['op'][1]['memo']
        except:
            return None
# end BlogHistoryEntry()

'''
Stand-alone methods.
'''
