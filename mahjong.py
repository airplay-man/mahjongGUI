# -*- coding: utf-8 -*-
'''
麻雀の結果を記録するGUIです
'''

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as messagebox
import tkinter.font as font
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import mod.calculate as cal
import mod.kanji as kanji
import mod.tkintertool_ima as tkima

PATH = os.path.dirname(os.path.abspath(__file__))

S = ["average rank", "total points", "top %", "rentai %", "not las %"]
F = ["average rank", "total points", "las %", "rentai %", "not top %"]
POSITION = [[6, 1], [3, 2], [0, 1], [3, 0]]
DIRECTION_img = ['ton', 'nan', 'sya', 'pe']

k = kanji.Kanji(path=PATH)
TENSU_KEISAN = k.TENSU_KEISAN
RULE_2 = k.RULE_2
YAKUMAN = k.YAKUMAN
TIER_S = k.TIER_S
TIER_F = k.TIER_F
TAB_WORD = k.TAB_WORD
TITLE = k.TITLE
RECORD = k.RECORD

class Application(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        master.title(TITLE)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.button_reload = tk.Button(master, text="reload", command=self._reload)
        self.button_reload.grid(row=1, column=0)
        self.tab_input = tk.Frame(self)
        self.tab_graph = tk.Frame(self)
        self.tab_records = tk.Frame(self)
        self.tab_scores = tk.Frame(self)
        self.tab_rule = tk.Frame(self)
        self.tab_full = tk.Frame(self)
        self.tab_seisan = tk.Frame(self)
        self.add(self.tab_input, text=TAB_WORD[0], padding=2)
        self.add(self.tab_graph, text=TAB_WORD[1], padding=2)
        self.add(self.tab_records, text=TAB_WORD[2], padding=2) #平均着順など
        self.add(self.tab_scores, text=TAB_WORD[3], padding=2) #全ての成績
        self.add(self.tab_rule, text=TAB_WORD[4], padding=2)
        self.add(self.tab_full, text=TAB_WORD[5], padding=2)
        self.add(self.tab_seisan, text=TAB_WORD[6], padding=2)
        self.grid(row=0, column=0)

        self.attach_scrollbar(master=self.tab_scores)

        self.history = -1

        self.read_sys_grand()

        self.set_tab_input_init()
        self.grid_tab_input_init()
        self.set_tab_rule_init()
        self.grid_tab_rule_init()
        self.grid_tab_record_init()
        self.set_tab_full_init()
        self.grid_tab_full_init()
        self.set_tab_seisan_init()
        self.grid_tab_seisan_init()

    def read_sys_grand(self):
        '''
        /sys/_grandより取り込む

        self.groups:全グループ名のリスト
        '''
        self.groups = []
        with open(PATH+'/sys/_grand/group.txt', 'r') as f:
            self.groups = self.rejectLF(f.readlines())

    def set_tab_input_init(self):
        '''
        self.tab_inputのグループによらない部分
        grid_tab_input_init()で配置する
        '''
        #グループ名を入れるCombobox
        self.frame_group = tk.Frame(self.tab_input)
        self.combo_group = ttk.Combobox(self.frame_group, value=tuple(self.groups), width=15, justify=tk.CENTER)
        self.combo_group.bind("<<ComboboxSelected>>", self.group_selected)
        self.button_group = tk.Button(self.frame_group, text='make', command=self.make_new_group)
        #プレイヤー名を入れるComboboxと点数を入れるEntry
        self.frame_players = tk.Frame(self.tab_input)
        self.img_directions = []
        for i in range(4):
            image = Image.open(PATH+"/sys/_grand/image/"+DIRECTION_img[i]+".png")
            image = image.resize((30, 30), Image.ANTIALIAS)
            self.img_directions.append(ImageTk.PhotoImage(image))
        self.combo_players = [ttk.Combobox(self.frame_players, width=8, justify=tk.CENTER) for i in range(4)]
        self.bind_for_tenho()
        self.entries_inputscores = [tk.Entry(self.frame_players, width=8, justify=tk.CENTER) for i in range(4)]
        #この試合が何試合目かを表示するカウンター
        self.num_game_counter = tk.StringVar()
        #入力決定ボタン
        self.frame_savescores = tk.Frame(self.tab_input)
        self.button_savescores = tk.Button(self.frame_savescores, text="save", width=5, command=self.savescores)

    def grid_tab_input_init(self):
        self.tab_input.grid_rowconfigure(0, minsize=20)
        self.tab_input.grid_columnconfigure((0, 2), weight=1)

        self.frame_group.grid(row=1, column=1)
        tk.Label(self.frame_group, text="group").grid(row=0, column=0)
        self.combo_group.grid(row=0, column=1)
        self.button_group.grid(row=0, column=2)

        self.tab_input.grid_rowconfigure(2, minsize=20)

        self.frame_players.grid(row=3, column=1)
        for i in range(4):
            tk.Label(self.frame_players, image=self.img_directions[i]).grid(row=POSITION[i][0], column=POSITION[i][1])
        for i in range(4):
            self.combo_players[i].grid(row=POSITION[i][0]+1, column=POSITION[i][1])
        for i in range(4):
            self.entries_inputscores[i].grid(row=POSITION[i][0]+2, column=POSITION[i][1])

        self.tab_input.grid_rowconfigure(4, minsize=70)

        tk.Label(self.tab_input, textvariable=self.num_game_counter).grid(row=5, column=1)

        self.frame_savescores.grid(row=6, column=1)
        self.button_savescores.grid(row=0, column=0)

    def set_tab_rule_init(self):
        '''
        self.tab_ruleのグループによらない部分
        grid_tab_rule_init()で配置する
        '''
        self.frame_rules = tk.Frame(self.tab_rule)
        #ウマ・オカ入力Entry
        self.entry_uma1 = tk.Entry(self.frame_rules, width=8)
        self.entry_uma2 = tk.Entry(self.frame_rules, width=8)
        self.entry_uma3 = tk.Entry(self.frame_rules, width=8)
        self.entry_uma4 = tk.Entry(self.frame_rules, width=8)
        #何点返しか入力Entry
        self.entry_gaeshi = tk.Entry(self.frame_rules, width=8)
        #その他細かい取り決め入力Txtbox
        self.txtbox_rule_2 = tk.Text(self.frame_rules, undo=True, wrap=tk.WORD, width=50)
        #これらを保存するボタン
        self.button_saverule = tk.Button(self.tab_rule, text="save", command=self.saverule)

    def grid_tab_rule_init(self):
        self.tab_rule.grid_rowconfigure(0, minsize=5)
        self.tab_rule.grid_columnconfigure((0, 2), weight=1)
        self.frame_rules.grid(row=1, column=1)
        self.frame_rules.grid_columnconfigure(1, minsize=10)
        self.frame_rules.grid_columnconfigure(3, minsize=30)
        tk.Label(self.frame_rules, text=TENSU_KEISAN[0]).grid(row=0, column=0)
        self.entry_uma1.grid(row=0, column=2, sticky='w')
        tk.Label(self.frame_rules, text=TENSU_KEISAN[1]).grid(row=1, column=0)
        self.entry_uma2.grid(row=1, column=2, sticky='w')
        tk.Label(self.frame_rules, text=TENSU_KEISAN[2]).grid(row=2, column=0)
        self.entry_uma3.grid(row=2, column=2, sticky='w')
        tk.Label(self.frame_rules, text=TENSU_KEISAN[3]).grid(row=3, column=0)
        self.entry_uma4.grid(row=3, column=2, sticky='w')
        tk.Label(self.frame_rules, text=TENSU_KEISAN[4]).grid(row=4, column=0)
        self.entry_gaeshi.grid(row=4, column=2, sticky='w')
        self.txtbox_rule_2.grid(row=0, column=4, rowspan=5)
        self.tab_rule.grid_rowconfigure(2, minsize=5)
        self.button_saverule.grid(row=3, column=1)

    def set_tab_full_init(self):
        '''
        self.tab_fullのグループによらない部分
        grid_tab_full_init()で配置する
        '''
        #役とアガった人を表示する表部分
        self.frame_yaku = tk.Frame(self.tab_full)
        #人を追加するボタン
        self.button_yaku = tk.Button(self.tab_full, text="add", command=self.add_full)

    def grid_tab_full_init(self):
        self.tab_full.grid_rowconfigure(0, minsize=20)
        self.tab_full.grid_columnconfigure((0, 2), weight=1)
        self.frame_yaku.grid(row=1, column=1)
        self.frame_yaku.grid_columnconfigure(1, minsize=10)
        self.tab_full.grid_rowconfigure(2, minsize=20)
        self.button_yaku.grid(row=3, column=1)

    def grid_tab_record_init(self):
        '''
        平均着順1位などの記録を表示する
        ラベル内のtk.StringVar()を更新するシステム
        set_tab_record_initはない
        '''
        for i in range(5):
            self.tierS_num = [tk.StringVar() for i in range(5)]
            self.tierS_person = [tk.StringVar() for i in range(5)]
            self.tierF_num = [tk.StringVar() for i in range(5)]
            self.tierF_person = [tk.StringVar() for i in range(5)]
        self.grid_tab_record_init_tier()
        self.frame_records = tk.Frame(self.tab_records)
        self.frame_records.grid(row=4, column=1, columnspan=3)


    def grid_tab_record_init_tier(self):
        '''
        grid_tab_record_init()で、成績優秀者とその逆に関するもの
        '''
        self.tab_records.grid_rowconfigure(0, minsize=10)
        self.tab_records.grid_columnconfigure((0, 4), weight=1)
        self.tab_records.grid_columnconfigure(2, minsize=10)
        tk.Label(self.tab_records, text="tier S").grid(row=1, column=1, sticky='w')
        frameS = tk.Frame(self.tab_records, highlightthickness=2, highlightbackground='plum')
        frameS.grid(row=2, column=1)
        frameS.grid_columnconfigure((1, 3), minsize=10)
        tk.Label(self.tab_records, text="tier F").grid(row=1, column=3, sticky='w')
        frameF = tk.Frame(self.tab_records, highlightthickness=2, highlightbackground='LightSkyBlue1')
        frameF.grid(row=2, column=3)
        frameF.grid_columnconfigure((1, 3), minsize=10)

        for i in range(5):
            tk.Label(frameS, text=TIER_S[i]).grid(row=i, column=0)
            tk.Label(frameS, textvariable=self.tierS_num[i]).grid(row=i, column=2)
            tk.Label(frameS, textvariable=self.tierS_person[i]).grid(row=i, column=4)
        for i in range(5):
            tk.Label(frameF, text=TIER_F[i]).grid(row=i, column=0)
            tk.Label(frameF, textvariable=self.tierF_num[i]).grid(row=i, column=2)
            tk.Label(frameF, textvariable=self.tierF_person[i]).grid(row=i, column=4)

    def set_tab_seisan_init(self):
        '''
        self.tab_seisanのグループによらない部分
        grid_tab_seisan_init()で配置する
        '''
        self.frame_ratesetting = tk.Frame(self.tab_seisan)
        self.combo_whichgame = ttk.Combobox(self.frame_ratesetting, width=8, justify=tk.CENTER)
        self.entry_rate = tk.Entry(self.frame_ratesetting, width=8)
        self.entry_rate.insert(0, '50')
        self.button_seisan = tk.Button(self.tab_seisan, text="cal", command=self.seisan)
        self.frame_seisan = tk.Frame(self.tab_seisan)

    def grid_tab_seisan_init(self):
        self.tab_seisan.grid_rowconfigure(0, minsize=20)
        self.tab_seisan.grid_columnconfigure((0, 2), weight=1)
        self.frame_ratesetting.grid(row=1, column=1)
        self.frame_ratesetting.grid_columnconfigure(1, minsize=10)
        tk.Label(self.frame_ratesetting, text="game").grid(row=0, column=0)
        self.combo_whichgame.grid(row=0, column=2, pady=5)
        tk.Label(self.frame_ratesetting, text="rate").grid(row=1, column=0)
        self.entry_rate.grid(row=1, column=2, pady=5)

        self.tab_seisan.grid_rowconfigure(2, minsize=20)
        self.button_seisan.grid(row=3, column=1)

        self.tab_seisan.grid_rowconfigure(4, minsize=20)
        self.frame_seisan.grid(row=5, column=1)

    def group_selected(self, event):
        '''
        グループを選択した時に発動する
        '''
        if self.combo_group.get() not in self.groups:
            print("group not exist")
            return
        print(self.combo_group.get()+" selected")
        #さっきまで表示されてたデータを削除
        self.clear()
        #そのグループの対戦データ以外のデータを取得
        self.read_group_sys()
        #そのグループの対戦データを取得
        self.read_group_data()
        #プレイヤー名候補をそのグループの人たちに更新
        self.set_value_of_combo_players()
        #ルールをそのグループのものに更新
        self.set_value_of_rules()
        #清算ページの設定
        self.set_value_of_combo_whichgame()
        #役満リストを更新
        self.grid_full_labels()
        #以下は対戦データがある場合
        if self.datas != []:
            #計算モジュールへ送るルールをまとめる
            self.get_rules()
            #計算
            self.cal_total()
            #グラフ表示
            self.show_graph()
            #平均着順1位などの項目をGUI上で更新
            self.reload_record()
            #平均着順などの項目を表示
            self.grid_records()
            #対戦生データを更新
            self.grid_scores()

    def read_group_sys(self):
        '''
        そのグループの対戦データ以外のデータを取得

        self.members:メンバーのリスト(list(str))
        self.history:対戦回数(int)
        self.rule:[uma1, uma2, uma3, uma4, gaeshi](list(str))
        self.rule_2:細かい取り決めのテキスト(str)
        self.fulls:役満達成リスト(list(str))

        self.fulls
            役満の数だけ行があり、各行に達成した人がコンマ区切りで書いてある
            各行がどの役満に当たるかは/sys/_grand/full.txt参照
        '''
        self.members = []
        self.history = 0
        self.rule = []
        self.rule_2 = ''
        self.fulls = []

        g = self.combo_group.get()
        with open(PATH+'/sys/'+g+'/member.txt', 'r') as f:
            self.members = self.rejectLF(f.readlines())
        with open(PATH+'/sys/'+g+'/history.txt', 'r') as f:
            self.history = int(self.rejectLF(f.readlines())[0])
        self.num_game_counter.set("#"+str(self.history+1))
        with open(PATH+'/sys/'+g+'/rule.txt', 'r') as f:
            self.rules = self.rejectLF(f.readlines())
        with open(PATH+'/sys/'+g+'/rule_2.txt', 'r') as f:
            r2 = f.readlines()
        for line in r2:
            self.rule_2 += line
        with open(PATH+'/sys/'+g+'/full.txt', 'r') as f:
            self.fulls = self.rejectLF(f.readlines())

    def read_group_data(self):
        '''
        そのグループの対戦データを取得

        self.data:対戦データ(list(list(str), list(str)))

        self.data
            [[player1, player2, player3, player4], [point, point, point, point]]
            というリストが対戦回分入っている
        '''
        self.datas = []

        g = self.combo_group.get()
        for i in range(self.history):
            with open(PATH+'/data/'+g+'/'+str(i+1)+'.txt', 'r') as f:
                data = self.rejectLF(f.readlines())
            for j in range(2):
                data[j] = data[j].split('\t')
            self.datas.append(data)

    def set_value_of_combo_players(self):
        '''
        プレイヤー名候補をそのグループの人たちに更新
        '''
        for i in range(4):
            self.combo_players[i].config(value=tuple(self.members))

    def set_value_of_rules(self):
        '''
        ルールをそのグループのものに更新
        '''
        self.entry_uma1.insert(0, self.rules[0])
        self.entry_uma2.insert(0, self.rules[1])
        self.entry_uma3.insert(0, self.rules[2])
        self.entry_uma4.insert(0, self.rules[3])
        self.entry_gaeshi.insert(0, self.rules[4])
        self.txtbox_rule_2.config(height=(self.rule_2.count('\n')+1))
        self.txtbox_rule_2.insert(tk.END, self.rule_2)

    def set_value_of_combo_whichgame(self):
        '''
        グループを選んだ際、清算ページの試合番号を選ぶComboboxの選択肢を用意
        '''
        if self.history == 0:
            self.combo_whichgame.config(value=())
        else:
            self.combo_whichgame.config(value=tuple(reversed(range(1, self.history+1))))
        self.combo_whichgame.delete(0, tk.END)
        if self.history != 0:
            self.combo_whichgame.insert(0, "latest")

    def savescores(self):
        '''
        対戦結果を入力決定した時に発動する関数
        '''
        if self.checkerror_savescores() == False:
            return
        self.history += 1
        print("game "+str(self.history)+" finished")
        self.num_game_counter.set("#"+str(self.history+1))
        self.savescores_data()
        self.savescores_sys()
        self.reload()

    def savescores_data(self):
        '''
        self.dataを保存
        新メンバーの保存はcheckerror_savescores()内
        '''
        result = ''
        for i in range(4):
            result += self.combo_players[i].get()
            if i != 3:
                result += '\t'
            else:
                result += '\n'
        for i in range(4):
            result += self.entries_inputscores[i].get().replace(' ', '')

            if i != 3:
                result += '\t'
        path = PATH+"/data/"+self.combo_group.get()+'/'+str(self.history)+'.txt'
        with open(path, 'w') as f:
            f.write(result)

    def savescores_sys(self):
        '''
        self.historyを保存
        '''
        path = PATH+"/sys/"+self.combo_group.get()+'/history.txt'
        with open(path, 'w') as f:
            f.write(str(self.history))

    def checkerror_savescores(self):
        '''
        データ入力ミスを防ぐ関数
        add_new_member()で新メンバーの保存は行なっている
        '''
        players = []
        goukei = 0
        if self.combo_group.get() not in self.groups:
            print("group not exist")
            return False
        self.add_new_member()
        for i in range(4):
            if self.combo_players[i].get() == '':
                print("error (player < 4)")
                return False
            if self.entries_inputscores[i].get() == '':
                print("error (score blank)")
                return False
            players.append(self.combo_players[i].get())
            goukei += int(self.entries_inputscores[i].get())
        if len(set(players)) != 4:
            print("error (1 player double count)")
            return False
        if goukei != 100000:
            print("error (not 100000 point)")
            return False
        return True

    def saverule(self):
        '''
        ルールの保存
        '''
        g = self.combo_group.get()
        if g not in self.groups or g == '':
            print("please select group")
            return

        dummy_rules = ''
        dummy_rules += self.entry_uma1.get().replace(' ', '')
        dummy_rules += "\n"
        dummy_rules += self.entry_uma2.get().replace(' ', '')
        dummy_rules += "\n"
        dummy_rules += self.entry_uma3.get().replace(' ', '')
        dummy_rules += "\n"
        dummy_rules += self.entry_uma4.get().replace(' ', '')
        dummy_rules += "\n"
        dummy_rules += self.entry_gaeshi.get().replace(' ', '')
        with open(PATH+'/sys/'+g+'/rule.txt', 'w') as f:
            f.write(dummy_rules)

        dummy_rule_2 = self.txtbox_rule_2.get('1.0', 'end -1c')
        with open(PATH+'/sys/'+g+'/rule_2.txt', 'w') as f:
            f.write(dummy_rule_2)

        print("rules saved")


    def rejectLF(self, list):
        '''
        listの各要素の右端にある改行を取り払う
        '''
        result = [line.rstrip('\n') for line in list]
        return result

    def make_new_group(self):
        '''
        新グループ作成ボタンを押した時発動

        _make_new_group()でグループ名の保存を行って
        make_new_dirs()でフォルダを作って
        サンプルの設定を一斉に作ってから
        clear()でそれまでのデータを決して

        サンプルを読み込んで
        read_group_sys()
        set_value_of_combo_players()
        set_value_of_rules()を行う
        '''
        if self.checkerror_make_new_group() == False:
            return
        self._make_new_group()
        self.make_new_dirs()
        g = self.combo_group.get().replace(' ', '')
        print("new group "+g)
        path = PATH + '/sys/' + g + '/rule.txt'
        with open(path, 'w') as f:
            f.write("20\n10\n-10\n-20\n30000")
        path = PATH + '/sys/' + g + '/rule_2.txt'
        with open(path, 'w') as f:
            f.write(RULE_2)
        path = PATH + '/sys/' + g + '/history.txt'
        with open(path, 'w') as f:
            f.write("0")
        path = PATH + '/sys/' + g + '/member.txt'
        with open(path, 'w') as f:
            f.write("")
        path = PATH + '/sys/' + g + '/full.txt'
        with open(path, 'w') as f:
            f.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        self.clear()
        self.members = []
        self.datas = []
        self.read_group_sys()
        self.set_value_of_combo_players()
        self.set_value_of_rules()
        self.set_value_of_combo_whichgame()

    def _make_new_group(self):
        '''
        新しいグループ名の保存
        '''
        g = self.combo_group.get().replace(' ', '')
        self.groups.append(g)
        self.combo_group.config(value=tuple(self.groups))
        result = ''
        n = len(self.groups)
        for i in range(n):
            result += self.groups[i]
            if i != (n - 1):
                result += '\n'
        path = PATH + '/sys/_grand/group.txt'
        with open(path, 'w') as f:
            f.write(result)

    def add_new_member(self):
        '''
        self.membersにいないメンバーが入力された場合にその人を
        self.membersに追加し、グループのデータにも保存
        '''
        for i in range(4):
            m = self.combo_players[i].get().replace(' ', '')
            if m not in self.members and m != '':
                self.members.append(m)
                print("new member "+m)
        path = PATH + '/sys/' + self.combo_group.get() + '/member.txt'
        result = ''
        for i in range(len(self.members)):
            result += self.members[i]
            if i != (len(self.members)-1):
                result += '\n'
        with open(path, 'w') as f:
            f.write(result)

    def checkerror_make_new_group(self):
        '''
        新グループ作成のエラー防止
        '''
        if self.combo_group.get() in self.groups:
            print('group already exists')
            return False
        if self.combo_group.get() == '':
            print('no input')
            return False

    def make_new_dirs(self):
        '''
        新グループのフォルダを作る
        '''
        g = self.combo_group.get().replace(' ', '')
        path = PATH + '/data/' + g
        os.mkdir(path)
        path = PATH + '/sys/' + g
        os.mkdir(path)

    def get_rules(self):
        '''
        計算モジュールへ送るルールをまとめる
        '''
        self.umaoka = [int(self.entry_uma1.get().replace(' ', '')), int(self.entry_uma2.get().replace(' ', '')), int(self.entry_uma3.get().replace(' ', '')), int(self.entry_uma4.get().replace(' ', ''))]
        self.gaeshi = int(self.entry_gaeshi.get().replace(' ', ''))

    def cal_total(self):
        '''
        計算
        '''
        self.cal_result = cal.Calculate(datas=self.datas, members=self.members, umaoka=self.umaoka, gaeshi=self.gaeshi)

    def reload(self):
        '''
        対戦結果を入力した時GUIを更新する
        全ての関数を走らせるようなもの
        グループを選んだ時とほとんど一緒
        '''
        self.clear()
        self.read_group_sys()
        self.read_group_data()
        self.set_value_of_combo_players()
        self.set_value_of_rules()
        self.get_rules()
        self.cal_total()
        self.show_graph()
        self.reload_record()
        self.grid_records()
        self.grid_scores()
        self.grid_full_labels()
        self.set_value_of_combo_whichgame()

    def _reload(self):
        '''
        reloadとほとんど一緒だが、clear部分が違う
        設定などは更新されないで成績系だけが更新されるようになっている
        '''
        if self.combo_group.get() == '' or self.combo_group.get() not in self.groups:
            print('group error')
            return
        self.grid_full_labels()
        if self.datas != []:
            self.clear_graph()
            self.clear_scores()
            self.clear_records()
            self.clear_seisan()
            self.get_rules()
            self.cal_total()
            self.show_graph()
            self.reload_record()
            self.grid_records()
            self.grid_scores()

    def clear(self):
        '''
        全て消し去る

        self.clear_graph()
        self.clear_scores()
        self.clear_records()
        self.clear_fulls()
        に加えて、ルール系が消える
        '''
        self.entry_uma1.delete(0, tk.END)
        self.entry_uma2.delete(0, tk.END)
        self.entry_uma3.delete(0, tk.END)
        self.entry_uma4.delete(0, tk.END)
        self.entry_gaeshi.delete(0, tk.END)
        self.txtbox_rule_2.delete("1.0", "end")
        for i in range(4):
            self.combo_players[i].delete(0, tk.END)
            self.entries_inputscores[i].delete(0, tk.END)
        self.clear_graph()
        self.clear_scores()
        self.clear_records()
        self.clear_fulls()
        self.clear_seisan()

    def show_graph(self):
        '''
        グラフ表示まとめ
        '''
        plt.rcParams["xtick.direction"] = "in" #x軸の目盛線を内向きへ
        plt.rcParams["ytick.direction"] = "in" #y軸の目盛線を内向きへ
        self.get_graphrange()
        self.set_graph()
        self.ax.autoscale(enable=True, axis='y')
        self.grid_graph()

    def get_graphrange(self):
        '''
        グラフのレンジを決める
        y軸はax.autoscale()に任せることにしたのでコメントアウトしている
        '''
        self.xend = self.history + 1
        # self.ystart = 0
        # self.yend = 0
        # for member in self.members:
        #     for i in range(self.xend):
        #         if self.cal_result.graphdata[member][i][1] < self.ystart:
        #             self.ystart = self.cal_result.graphdata[member][i][1]
        #         if self.cal_result.graphdata[member][i][1] > self.yend:
        #             self.yend = self.cal_result.graphdata[member][i][1]
        # self.ystart = int(self.ystart) - 20
        # self.yend = int(self.yend) + 20

    def set_graph(self):
        '''
        matplotlib的なグラフの設定を決める
        '''
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.yaxis.set_ticks_position('both')
        self.ax.xaxis.set_ticks_position('both')
        self.ax.tick_params(axis='x', which='major', labelsize=12)
        self.ax.tick_params(axis='y', which='major', labelsize=12)
        self.ax.set_ylabel("total points", fontsize=12)
        self.ax.set_xlabel("times", fontsize=12)
        self.ax.set_xlim(0, self.xend)
        # self.ax.set_ylim(self.ystart, self.yend)
        #ここでプロット
        for member in self.members:
            xdata = [row[0] for row in self.cal_result.graphdata[member]]
            ydata = [row[1] for row in self.cal_result.graphdata[member]]
            self.ax.plot(xdata, ydata, marker='o', linestyle='solid', linewidth=1, markersize=3, label=member)
        self.ax.legend()
        self.ax.axhline(y=0, color='black', linewidth=1, linestyle='dotted')

    def grid_graph(self):
        '''
        グラフをGUIに表示
        '''
        canvas = FigureCanvasTkAgg(self.fig, master=self.tab_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.tab_graph)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def clear_graph(self):
        '''
        グラフページを一掃
        '''
        for child in self.tab_graph.winfo_children():
            child.destroy()

    def reload_record(self):
        '''
        平均着順1位などの記録を更新する
        ラベル内のtk.StringVar()を更新するシステム
        '''
        for i in range(5):
            if i == 0:
                self.tierS_num[i].set(round(self.cal_result.tierS[S[i]][1], 2))
                self.tierS_person[i].set(self.cal_result.tierS[S[i]][0])
                self.tierF_num[i].set(round(self.cal_result.tierF[F[i]][1], 2))
                self.tierF_person[i].set(self.cal_result.tierF[F[i]][0])
            else:
                self.tierS_num[i].set(round(self.cal_result.tierS[S[i]][1], 1))
                self.tierS_person[i].set(self.cal_result.tierS[S[i]][0])
                self.tierF_num[i].set(round(self.cal_result.tierF[F[i]][1], 1))
                self.tierF_person[i].set(self.cal_result.tierF[F[i]][0])

    def clear_records(self):
        '''
        平均着順1位などの記録を白紙にする
        '''
        for i in range(5):
            self.tierS_num[i].set('')
            self.tierS_person[i].set('')
            self.tierF_num[i].set('')
            self.tierF_person[i].set('')
        for child in self.frame_records.winfo_children():
            child.destroy()

    def grid_scores(self):
        '''
        対戦生データの表示
        '''
        self.scrframe.grid_rowconfigure(0, minsize=10)
        self.scrframe.grid_columnconfigure((0, len(self.members)+3), weight=1)
        self.scrframe.grid_columnconfigure(2, minsize=5)
        for_index = dict()
        for i, member in enumerate(self.members):
            for_index[member] = i+3
            tk.Label(self.scrframe, text=member, highlightthickness=2, highlightbackground='lightseagreen').grid(row=1, column=i+3)
        for k, game in enumerate(self.datas):
            tk.Label(self.scrframe, text=str(k+1), highlightthickness=2, highlightbackground='gray', width=2).grid(row=k+2, column=1)
            for i in range(4):
                tk.Label(self.scrframe, text=game[1][i]).grid(row=k+2, column=for_index[game[0][i]])

    def grid_records(self):
        '''
        grid_tab_record_init()で全員のを表示する
        '''
        self.tab_records.grid_rowconfigure(3, minsize=20)
        self.frame_records.grid_columnconfigure((0, len(self.members)+3), weight=1)
        self.frame_records.grid_columnconfigure(2, minsize=5)
        for_index = dict()
        for i, member in enumerate(self.members):
            for_index[member] = i+3
            tk.Label(self.frame_records, text=member).grid(row=0, column=i+3)
        for i in range(len(RECORD)):
            tk.Label(self.frame_records, text=RECORD[i]).grid(row=i+1, column=1)
        for member in self.members:
            tk.Label(self.frame_records, text=str(round(self.cal_result.heikin_chakujun[member], 2))).grid(row=1, column=for_index[member])
            tk.Label(self.frame_records, text=str(round(self.cal_result.per_rentai[member], 1))).grid(row=2, column=for_index[member])
            tk.Label(self.frame_records, text=str(round(self.cal_result.per_top[member], 1))).grid(row=3, column=for_index[member])
            tk.Label(self.frame_records, text=str(round(self.cal_result.per_las[member], 1))).grid(row=4, column=for_index[member])
            tk.Label(self.frame_records, text=str(round(self.cal_result.seiseki[member], 1))).grid(row=5, column=for_index[member])

    def clear_scores(self):
        '''
        対戦生データの削除
        '''
        for child in self.scrframe.winfo_children():
            child.destroy()

    def clear_seisan(self):
        '''
        清算結果の削除
        '''
        for child in self.frame_seisan.winfo_children():
            child.destroy()

    def grid_full_labels(self):
        '''
        役満達成者の表示
        self.frame_yaku上で行う
        '''
        self.clear_fulls()
        for i in range(len(YAKUMAN)):
            tk.Label(self.frame_yaku, text=YAKUMAN[i]).grid(row=i, column=0, sticky='n')
        for i in range(len(self.fulls)):
            line = ''
            if self.fulls[i] != '':
                line = self.fulls[i].split(',')
            if line != ['']:
                if len(line) == 1:
                    tk.Label(self.frame_yaku, text=line[0]).grid(row=i, column=2)
                elif len(line) > 1:
                    frame = tk.Frame(self.frame_yaku)
                    frame.grid(row=i, column=2)
                    for j in range(len(line)):
                        tk.Label(frame, text=line[j]).grid(row=j, column=0)

    def add_full(self):
        '''
        役満達成者が現れた場合の関数
        ポップアップウインドウが出てきて、役と人を入力しokを押す
        '''
        if self.history == -1:
            print('which group ?')
            return
        self.window_add_full = tk.Toplevel()
        self.combo_add_full_yaku = ttk.Combobox(self.window_add_full, value=tuple(YAKUMAN), state='readonly')
        self.combo_add_full_yaku.grid(row=0, column=0)
        self.combo_add_full_member = ttk.Combobox(self.window_add_full, value=tuple(self.members), state='readonly')
        self.combo_add_full_member.grid(row=1, column=0)
        tk.Button(self.window_add_full, text='ok', command=self._add_full).grid(row=2, column=0)

    def _add_full(self):
        '''
        上の関数でokを押すとself.fullを更新したのち
        grid_full_labels()でGUIを更新して、save_fulls()でデータも保存する
        '''
        if self.combo_add_full_yaku.get() == '':
            print('which ?')
            del self.combo_add_full_yaku, self.combo_add_full_member
            self.window_add_full.destroy()
            return
        if self.combo_add_full_member.get() == '':
            print('who ?')
            del self.combo_add_full_yaku, self.combo_add_full_member
            self.window_add_full.destroy()
            return
        for i in range(len(YAKUMAN)):
            if YAKUMAN[i] == self.combo_add_full_yaku.get():
                if self.fulls[i] != '':
                    self.fulls[i] += ','
                self.fulls[i] += self.combo_add_full_member.get()
        del self.combo_add_full_yaku, self.combo_add_full_member
        self.window_add_full.destroy()
        self.grid_full_labels()
        self.save_fulls()

    def save_fulls(self):
        '''
        役満達成者の保存
        '''
        result = ''
        for i in range(len(self.fulls)):
            result += self.fulls[i]
            if i != (len(self.fulls) - 1):
                result += '\n'
        path = PATH + '/sys/' + self.combo_group.get() + '/full.txt'
        with open(path, 'w') as f:
            f.write(result)

    def clear_fulls(self):
        '''
        役満達成者ページの一掃
        '''
        for child in self.frame_yaku.winfo_children():
            child.destroy()

    def bind_for_tenho(self):
        '''
        グループ'tenho'の時は、meを基準にkami, toi, shimoを並べる
        その為にself.combo_playersをbindしておく
        '''
        for i in range(4):
            self.combo_players[i].bind("<<ComboboxSelected>>", self.player_selected_when_tenho(index=i))

    def player_selected_when_tenho(self, index):
        '''
        上記のbind内容
        '''
        def x(event):
            if self.combo_group.get() != 'tenho':
                return
            dummy = [1, 2, 3, 0, 1, 2]
            if self.combo_players[index].get() != 'me':
                return
            for i in range(3):
                self.combo_players[dummy[index+i]].current(i+1)
        return x

    def seisan(self):
        '''
        試合番号とレートを入力し、掛け算を行う
        '''
        self.clear_seisan()
        if self.combo_group.get() == '':
            print("no group selected")
            return
        if self.combo_whichgame.get() == '' or self.entry_rate.get() == '':
            print("can't calculate")
            return
        index = self.history - 1
        if self.combo_whichgame.get() != "latest":
            index = int(self.combo_whichgame.get()) - 1
        self.get_rules()
        result = cal.Calculate([self.datas[index]], self.datas[index][0], self.umaoka, self.gaeshi)
        for i in range(4):
            member = self.datas[index][0][i]
            tk.Label(self.frame_seisan, text=member, highlightthickness=2, highlightbackground='lightseagreen').grid(row=0, column=i, padx=5)
            tk.Label(self.frame_seisan, text=str(round(result.seiseki[member], 1))).grid(row=1, column=i)
            money = round(result.seiseki[member]) * int(self.entry_rate.get())
            tk.Label(self.frame_seisan, text=str(int(money))+'yen').grid(row=2, column=i)

    def attach_scrollbar(self, master=None):
        '''
        scrollbarつきframeのself.rightframeを作る
        '''
        canvas = tk.Canvas(master)
        tkima.grid_config(master, rlist=[[0, 'weight', 1]], clist=[[0, 'weight', 1]])

        bar = tk.Scrollbar(master, orient=tk.VERTICAL)
        bar.grid(row=0, column=1, sticky='ns')
        bar.config(command=canvas.yview)

        canvas.config(yscrollcommand=bar.set)
        canvas.config(scrollregion=(0, 0, canvas.winfo_reqwidth(), 3000))
        canvas.grid(row=0, column=0, sticky='news')

        self.scrframe = tk.Frame(canvas)
        canvas.create_window((0,0), window=self.scrframe, anchor=tk.NW)



if __name__ == "__main__":
    print("mahjong app started")
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()
