'''
Wrapper module for access to, and modification of, STEEM blockchain data.
Optimized by extensive use of generator functions and other means.
'''

from steem import *

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


    def get_steemd(self):
        return self.__steem.steemd

    def get_commit(self):
        return self.__steem.commit

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

            last_entry = sel_arr[len(sel_arr) - 1][0]
            
            for el in sel_arr: yield el

            if completion_flag: break

            index_from += limit
