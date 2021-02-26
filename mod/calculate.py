# -*- coding: utf-8 -*-
'''
mahjong.pyのための計算モジュール
'''

__author__ = 'Imawaka Hiroki'

import collections
import numpy as np

class Calculate():
    def __init__(self, datas, members, umaoka, gaeshi):
        '''
        self.data:対戦データ(list(list(str), list(str)))
        self.members:メンバーのリスト(list(str))
        self.umaoka:[uma1, uma2, uma3, uma4](list(str))
        self.gaeshi:30000とか(str)

        self.data
            [[player1, player2, player3, player4], [point, point, point, point]]
            というリストが対戦回分入っている
        '''
        self.datas = datas
        self.members = members
        self.umaoka = umaoka
        self.gaeshi = gaeshi

        self.num_game = dict() #試合数
        self.chakujun = dict() #その人の着順の履歴
        self.heikin_chakujun = dict() #平均着順
        self.tierS = dict() #5つの項目においてもっとも優れている人とその値
        self.tierF = dict() #5つの項目においてもっとも優れていない人とその値
        self.per_top = dict() #トップ率
        self.per_2nd = dict() #2位率
        self.per_3rd = dict() #3位率
        self.per_las = dict() #ラス率
        self.per_rentai = dict() #連帯率(1位2位率)
        self.per_not_top = dict() #トップじゃない率
        self.per_not_las = dict() #ラス回避率
        self.seiseki = dict() #成績の合計
        self.graphdata = dict() #グラフ用成績
        self.prepare()

        self.cal_num_game()
        self.cal_chakujun()
        self.cal_heikin_chakujun()
        self.cal_persentage()
        self.cal_seiseki()
        self.cal_tierS()
        self.cal_tierF()

    def prepare(self):
        '''
        各データの初期値
        '''
        for i in range(len(self.datas)):
            self.datas[i].append([0, 0, 0, 0])

        for member in self.members:
            self.num_game[member] = 0
            self.chakujun[member] = []
            self.heikin_chakujun[member] = 0
            self.per_top[member] = 0
            self.per_2nd[member] = 0
            self.per_3rd[member] = 0
            self.per_las[member] = 0
            self.per_rentai[member] = 0
            self.per_not_top[member] = 0
            self.per_not_las[member] = 0
            self.seiseki[member] = 0
            self.graphdata[member] = []

    def cal_num_game(self):
        '''
        メンバーごとに対戦回数をまとめる
        {"member1":int, "member2":int, ...}
        '''
        for game in self.datas:
            for i in range(4):
                self.num_game[game[0][i]] += 1

    def cal_heikin_chakujun(self):
        '''
        メンバーごとに平均着順をまとめる
        {"member1":float, "member2":float, ...}
        '''
        for member in self.members:
            for a in self.chakujun[member]:
                self.heikin_chakujun[member] += a

        for member in self.members:
            if self.num_game[member] == 0:
                self.heikin_chakujun[member] = 2.50
            else:
                self.heikin_chakujun[member] = self.heikin_chakujun[member] / self.num_game[member]

    def cal_chakujun(self):
        '''
        self.datasに3つ目の要素を追加する
        [[player1, player2, player3, player4], [point, point, point, point]]
        から
        [[player1, player2, player3, player4], [point, point, point, point], [rank, rank, rank, rank]]
        に(rankは着順で、1~4)

        さらにメンバーごとの着順の履歴をまとめる
        {"member1":int, "member2":int, ...}
        '''
        for k in range(len(self.datas)):
            sortdata = [int(ten) for ten in self.datas[k][1]]
            sortdata = sorted(sortdata, reverse=True)
            sortdata = [str(ten) for ten in sortdata]
            dummydata = []
            for j in range(4):
                dummydata.append(self.datas[k][1][j])
            for i in range(4):
                for j in range(4):
                    if sortdata[i] == self.datas[k][1][j]:
                        self.datas[k][2][j] = i+1
                        sortdata[i] = True
                        self.datas[k][1][j] = False
            self.datas[k][1] = dummydata
            for i in range(4):
                self.chakujun[self.datas[k][0][i]].append(self.datas[k][2][i])

    def cal_tierS(self):
        '''
        項目ごとに優秀者とその値をまとめる
        self.tierS =
        {"平均着順":float, "合計得点":float, "トップ率":float, "連帯率":float, "ラス回避率":float}
        '''
        min_heikin_chakujun = ['', 4]
        max_seiseki = ['', 0]
        max_per_top = ['', 0]
        max_per_rentai = ['', 0]
        max_per_not_las = ['', 0]
        for  member in self.members:
            if self.num_game[member] >= 2:
                if self.heikin_chakujun[member] < min_heikin_chakujun[1]:
                    min_heikin_chakujun = [member, self.heikin_chakujun[member]]
                if self.seiseki[member] > max_seiseki[1]:
                    max_seiseki = [member, self.seiseki[member]]
                if self.per_top[member] > max_per_top[1]:
                    max_per_top = [member, self.per_top[member]]
                if self.per_rentai[member] > max_per_rentai[1]:
                    max_per_rentai = [member, self.per_rentai[member]]
                if self.per_not_las[member] > max_per_not_las[1]:
                    max_per_not_las = [member, self.per_not_las[member]]
        self.tierS["average rank"] = min_heikin_chakujun
        self.tierS["total points"] = max_seiseki
        self.tierS["top %"] = max_per_top
        self.tierS["rentai %"] = max_per_rentai
        self.tierS["not las %"] = max_per_not_las

    def cal_tierF(self):
        '''
        項目ごとに優秀者とその値をまとめる
        self.tierF =
        {"平均着順":float, "合計得点":float, "ラス率":float, "連帯率":float, "トップじゃない率":float}
        '''
        max_heikin_chakujun = ['', 1]
        min_seiseki = ['', max(self.seiseki.values())]
        max_per_las = ['', 0]
        min_per_rentai = ['', max(self.per_rentai.values())]
        max_per_not_top = ['', 0]
        for  member in self.members:
            if self.num_game[member] >= 2:
                if self.heikin_chakujun[member] > max_heikin_chakujun[1]:
                    max_heikin_chakujun = [member, self.heikin_chakujun[member]]
                if self.seiseki[member] < min_seiseki[1]:
                    min_seiseki = [member, self.seiseki[member]]
                if self.per_las[member] > max_per_las[1]:
                    max_per_las = [member, self.per_las[member]]
                if self.per_rentai[member] < min_per_rentai[1]:
                    min_per_rentai = [member, self.per_rentai[member]]
                if self.per_not_top[member] > max_per_not_top[1]:
                    max_per_not_top = [member, self.per_not_top[member]]
        self.tierF["average rank"] = max_heikin_chakujun
        self.tierF["total points"] = min_seiseki
        self.tierF["las %"] = max_per_las
        self.tierF["rentai %"] = min_per_rentai
        self.tierF["not top %"] = max_per_not_top

    def cal_persentage(self):
        '''
        上の2関数の準備
        '''
        for member in self.members:
            if self.num_game[member] != 0:
                c = collections.Counter(self.chakujun[member])
                self.per_top[member] = c[1]*100/self.num_game[member]
                self.per_2nd[member] = c[2]*100/self.num_game[member]
                self.per_3rd[member] = c[3]*100/self.num_game[member]
                self.per_las[member] = c[4]*100/self.num_game[member]
                self.per_rentai[member] = self.per_top[member] + self.per_2nd[member]
                self.per_not_top[member] = 100 - self.per_top[member]
                self.per_not_las[member] = 100 - self.per_las[member]

    def cal_seiseki(self):
        '''
        メンバーごとに成績をまとめる
        self.seiseki =
        {"member1":float, "member2":float, ...}

        また、グラフ用に整理された配列も用意する
        self.graphdata =
        {"member1":[[int, float], ...]}
        参加してない試合も、成績推移なしとして値を持たせる
        '''
        for member in self.members:
            self.graphdata[member].append([0, 0])
        for k, game in enumerate(self.datas):
            for i in range(4):
                s = (int(game[1][i])-30000) / 1000
                s += self.umaoka[game[2][i]-1]
                self.seiseki[game[0][i]] += s
                if game[2][i] == 1:
                    self.seiseki[game[0][i]] += (self.gaeshi-25000)*4 / 1000
            for member in self.members:
                self.graphdata[member].append([k+1, self.seiseki[member]])

if __name__ == "__main__":
    a = [['a', 'b', 'c', 'd'],['21000', '22000', '35000', '18000']], [['b', 'c', 'd', 'e'], ['45800', '5100', '13000', '36100']]
    b = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    c = Calculate(datas=a, members=b, umaoka=[20, 10, -10, -20], gaeshi=30000)
    print(c.datas)
    # print(c.num_game)
    # print(c.heikin_chakujun)
    # print(c.chakujun)
    # print(c.per_rentai)
    # print(c.tierS)
    # print(c.tierF)
    # print(c.seiseki)
    # print(c.graphdata)
