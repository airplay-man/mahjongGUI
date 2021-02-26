# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.font as font

COLOR_BG = 'white'

'''
Widget系
'''

class Label(tk.Label):
    '''
    tk.Labelとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    '''
    def __init__(self, master, text='', textvariable=None, bg=COLOR_BG, justify='center', font=None, image=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        if textvariable == None:
            super().__init__(master, text=text, bg=bg, font=font, justify=justify)
        else:
            super().__init__(master, textvariable=textvariable, bg=bg, font=font, justify=justify)

        if image != None:
            self.config(image=image)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

class Frame(tk.Frame):
    '''
    tk.Frameとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    '''
    def __init__(self, master, bg=COLOR_BG, highlightthickness=0, highlightbackground='black', borderwidth=0, relief='flat', height=0, propagate=False, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, bg=bg, highlightthickness=highlightthickness, highlightbackground=highlightbackground, borderwidth=borderwidth, relief=relief, height=height)
        self.propagate(propagate)
        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

    def clear(self):
        '''
        frame内のwidgetを一掃する
        '''
        for child in self.winfo_children():
            child.destroy()

    def grid_config(self, rlist, clist):
        '''
        grid_rowconfigureとgrid_columnconfigureの合成
        rlist[i] = [num(or tuple), {arg : num}]
        '''
        for i in range(len(rlist)):
            if rlist[i][1] == 'minsize':
                self.grid_rowconfigure(rlist[i][0], minsize=rlist[i][2])
            if rlist[i][1] == 'weight':
                self.grid_rowconfigure(rlist[i][0], weight=rlist[i][2])
        for i in range(len(clist)):
            if clist[i][1] == 'minsize':
                self.grid_columnconfigure(clist[i][0], minsize=clist[i][2])
            if clist[i][1] == 'weight':
                self.grid_columnconfigure(clist[i][0], weight=clist[i][2])

class Button(tk.Button):
    '''
    tk.Buttonとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    '''
    def __init__(self, master, text='', command=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, text=text, command=command)
        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

class Entry(tk.Entry):
    '''
    tk.Entryとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    initはinsert()をする
    '''
    def __init__(self, master, width=20, justify=tk.CENTER, init=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, width=width, justify=justify)
        if init != None:
            self.insert(0, init)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)


    def overwrite(self, str):
        '''
        deleteしてinsertする流れをまとめたもの
        '''
        self.delete(0, tk.END)
        self.insert(0, str)

class Spinbox(tk.Spinbox):
    '''
    tk.Spinboxとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    initはinsert()をする
    '''
    def __init__(self, master, from_=1, to=10, increment=1, width=20, init=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, from_=from_, to=to, increment=increment, width=width)
        if init != None:
            self.delete(0, tk.END)
            self.insert(0, init)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

class Checkbutton(tk.Checkbutton):
    '''
    tk.Checkbuttonとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    '''
    def __init__(self, master, text='', variable=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, text=text, variable=variable)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

class Listbox(tk.Listbox):
    '''
    tk.Listboxとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    '''
    def __init__(self, master, height=10, selectmode='single', grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, height=height, selectmode=selectmode)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)

    def iteminsert(self, text='', fg='black', bg='white'):
        '''
        insert()とitemconfigure()をまとめたもの
        '''
        self.insert(tk.END, text)
        self.itemconfigure(tk.END, fg=fg, bg=bg)

class StringVar(tk.StringVar):
    '''
    tk.StringVarとsetの合成
    listは何かに格納する場合
    '''
    def __init__(self, set='', list=None):
        super().__init__()
        self.set(set)
        if list != None:
            list.append(self)

class BooleanVar(tk.BooleanVar):
    '''
    tk.BooleanVarとsetの合成
    listは何かに格納する場合
    '''
    def __init__(self, set=False, list=None):
        super().__init__()
        self.set(set)
        if list != None:
            list.append(self)

class Toplevel(tk.Toplevel):
    def __init__(self, title='', func_when_destroy=None):
        super().__init__()
        self.title(title)
        if func_when_destroy != None:
            self.bind("<Destroy>", func_when_destroy)

class Combobox(ttk.Combobox):
    '''
    ttk.Comboboxとgridの合成
    引数gridは、gridするかしないかを選べる
    listは何かに格納する場合
    initは、intならcurrent(), strならinsert()を行う
    bindは担当しないことにする
    '''
    def __init__(self, master, value=(), width=20, state='normal', justify=tk.CENTER, init=None, grid=True, row=0, column=0, sticky='', rowspan=1, columnspan=1, list=None):
        super().__init__(master, value=value, width=width, state=state, justify=justify)
        if type(init) == int:
            self.current(init)
        elif type(init) == str and state == 'normal':
            self.insert(0, init)

        if list != None:
            list.append(self)
            if grid:
                list[-1].grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)
        if list == None and grid:
            self.grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan)




'''
関数系(?)
'''

def grid_config(widget, rlist=[], clist=[]):
    '''
    grid_rowconfigureとgrid_columnconfigureの合成
    rlist[i] = [num(or tuple), {arg : num}]
    '''
    if rlist != []:
        for i in range(len(rlist)):
            if rlist[i][1] == 'minsize':
                widget.grid_rowconfigure(rlist[i][0], minsize=rlist[i][2])
            if rlist[i][1] == 'weight':
                widget.grid_rowconfigure(rlist[i][0], weight=rlist[i][2])
    if clist != []:
        for i in range(len(clist)):
            if clist[i][1] == 'minsize':
                widget.grid_columnconfigure(clist[i][0], minsize=clist[i][2])
            if clist[i][1] == 'weight':
                widget.grid_columnconfigure(clist[i][0], weight=clist[i][2])

def frameclear(parent):
    '''
    frame内のwidgetを一掃する
    frameを渡さないといけない
    '''
    for child in parent.winfo_children():
        child.destroy()

def frameforget(parent):
    '''
    frame内のwidgetをforget(grid解除)する
    frameを渡さないといけない
    '''
    for child in parent.winfo_children():
        child.grid_forget()
