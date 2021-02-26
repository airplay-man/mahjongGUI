# -*- coding: utf-8 -*-
'''
mahjong.pyのための語句呼び出しモジュール
'''

__author__ = 'Imawaka Hiroki'

import os

def rejectLF(list):
    '''
    listの各要素の右端にある改行を取り払う
    '''
    result = [line.rstrip('\n') for line in list]
    return result

class Kanji():
    def __init__(self, path):
        self.PATH = path + '/sys/_grand/'

        with open(self.PATH+'kanji/tensu_keisan.txt', 'r') as f:
            self.TENSU_KEISAN = rejectLF(f.readlines())

        self.RULE_2 = ''
        with open(self.PATH+'rule_2.txt', 'r') as f:
            r2 = f.readlines()
        for line in r2:
            self.RULE_2 += line

        with open(self.PATH+'kanji/full.txt', 'r') as f:
            self.YAKUMAN = rejectLF(f.readlines())

        with open(self.PATH+'kanji/tierS.txt', 'r') as f:
            self.TIER_S = rejectLF(f.readlines())

        with open(self.PATH+'kanji/tierF.txt', 'r') as f:
            self.TIER_F = rejectLF(f.readlines())

        with open(self.PATH+'kanji/tab.txt', 'r') as f:
            self.TAB_WORD = rejectLF(f.readlines())

        with open(self.PATH+'kanji/title.txt', 'r') as f:
            self.TITLE = rejectLF(f.readlines())

        with open(self.PATH+'kanji/record.txt', 'r') as f:
            self.RECORD = rejectLF(f.readlines())
