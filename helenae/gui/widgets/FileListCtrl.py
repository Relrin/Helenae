# -*- coding: utf-8 -*-
"""
    Custom widget for wxPython: file list control
"""
import wx
import os
import time
import platform
from math import log

unit_list = zip(['байт', 'Кб', 'Мб', 'Гб', 'Тб', 'Пб'], [0, 0, 1, 2, 2, 2])
def convertSize(num):
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 0:
        return '0 байт'
    elif num == 1:
        return '1 байт'


class FileListCtrl(wx.ListCtrl):

    def __init__(self, parent, id, ico_folder):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
        self.parent = parent

        self.currentDir = None
        self.defaultDir = None
        self.__path = ico_folder + '/icons/mimetypes/'
        images = [ico_folder + '/icons/empty.png', ico_folder + '/icons/mimetypes/folder.png', ico_folder + '/icons/ui/up16.png']
        types_icons = [self.__path + f for f in os.listdir(self.__path)]
        types_icons.sort()
        images += types_icons
        self.supported_types = [f.replace(self.__path,'').replace('.png', '') for f in types_icons if not f.endswith('folder.png')]

        # information about file in columns
        self.InsertColumn(0, 'Имя')
        self.InsertColumn(1, 'Тип')
        self.InsertColumn(2, 'Размер', wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(3, 'Посл. изменение')
        # size for every column by ID
        self.SetColumnWidth(0, 450)
        self.SetColumnWidth(1, 80)
        self.SetColumnWidth(2, 150)
        self.SetColumnWidth(3, 120)
        # add images for supported files
        self.il = wx.ImageList(16, 16)
        for i in images:
            self.il.Add(wx.Bitmap(i))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onLeftClick)

    def setCurrentDir(self, dir):
        self.currentDir = dir
        if not self.currentDir.endswith('/'):
            self.currentDir += '/'

    def setUsersDir(self, dir):
        self.defaultDir = dir
        if not self.defaultDir.endswith('/'):
            self.defaultDir += '/'

    def getUsersDir(self):
        return self.defaultDir

    def insertUpDirectory(self):
        #up from this folder to '..'
        self.InsertStringItem(0, '..')
        self.SetItemImage(0, 2)

    def showFilesInDirectory(self, directory='.'):
        self.parent.sb.SetStatusText(directory)
        self.DeleteAllItems()
        j = 0

        if directory != self.defaultDir:
            self.insertUpDirectory()
            j = 1

        # add at the and of our 'directory' string '/' if doesn't contain this symbol
        if not directory.endswith('/'):
            directory += '/'

        # all founded folders append first
        directories = [f for f in os.listdir(directory) if os.path.exists(directory+f) and os.path.isdir(directory+f)]
        directories.sort()

        for i in directories:
            sec = os.path.getmtime(directory+i)
            self.InsertStringItem(j, i)
            self.SetStringItem(j, 1, '')
            self.SetStringItem(j, 2, '')
            self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))
            self.SetItemImage(j, 1)
            if (j % 2) == 0:
                self.SetItemBackgroundColour(j, '#e6f1f5')
            j += 1

        # after append all files in directory
        files = [f for f in os.listdir(directory) if os.path.isfile(directory+f)]
        files.sort()

        for i in files:
            (name, ext) = os.path.splitext(i)
            ex = ext[1:]
            size = os.path.getsize(directory+i)
            sec = os.path.getmtime(directory+i)
            self.InsertStringItem(j, name)
            self.SetStringItem(j, 1, ex)
            self.SetStringItem(j, 2, convertSize(size))
            self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))

            # its supported type
            if ex in self.supported_types:
                index = self.supported_types.index(ex) + 4
                self.SetItemImage(j, index)
            # unsupported type; set "unknown ico"
            else:
                self.SetItemImage(j, 0)

            if (j % 2) == 0:
                self.SetItemBackgroundColour(j, '#e6f1f5')
            j += 1

    def ResizeColumns(self, sizeX):
        self.SetColumnWidth(0, sizeX * 0.5625)
        self.SetColumnWidth(1, sizeX * 0.1)
        self.SetColumnWidth(2, sizeX * 0.1875)
        self.SetColumnWidth(3, sizeX * 0.15)

    def getParentDir(self, dir):
        return os.sep.join(dir.split(os.sep)[:-2]) + '/'

    def onLeftClick(self, event):
        index = self.GetFirstSelected()
        filepath = self.currentDir + self.getFullnameItem(index)
        if os.path.isdir(filepath):
            if self.GetItem(index, 0).GetText() == '..':
                self.currentDir = self.getParentDir(self.currentDir)
                filepath = self.currentDir
                self.showFilesInDirectory(filepath)
            else:
                self.currentDir = filepath + '/'
                self.showFilesInDirectory(filepath)
        else:
            platform_os = platform.system()
            if platform_os == 'Linux':
                os.system('xdg-open "%s"' % (filepath))
            elif platform_os == 'Windows':
                os.system('start "%s"')

    def getFullnameItem(self, index):
        item = self.GetItem(index, 0).GetText()
        if self.GetItem(index, 1).GetText() != '':
            item += '.' + self.GetItem(index, 1).GetText()
        return item

    def getSelectedItems(self):
        selection = []
        index = self.GetFirstSelected()
        selection.append(self.getFullnameItem(index))
        if selection[0] in (u'', u'..'):
            return []
        while len(selection) != self.GetSelectedItemCount():
            index = self.GetNextSelected(index)
            if self.getFullnameItem(index) not in (u'', u'..'):
                selection.append(self.getFullnameItem(index))
        return selection