# -*- coding: utf-8 -*-
"""
    Custom widget for wxPython: file list control
"""

import wx
import os
import time


class FileListCtrl(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)

        self.__path = './gui/icons/mimetypes/'
        images = ['./gui/icons/empty.png', './gui/icons/mimetypes/folder.png', './gui/icons/ui/up16.png']
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
        self.SetColumnWidth(0, 160)
        self.SetColumnWidth(1, 50)
        self.SetColumnWidth(2, 70)
        self.SetColumnWidth(3, 120)
        # add images for supported files
        self.il = wx.ImageList(16, 16)
        for i in images:
            self.il.Add(wx.Bitmap(i))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        j = 1
        self.InsertStringItem(0, '..')
        self.SetItemImage(0, 2)

        # all founded folders append first
        directories = [f for f in os.listdir('.') if os.path.isdir(f)]
        directories.sort()
        directories = directories

        for i in directories:
            (name, ext) = os.path.splitext(i)
            ex = ext[1:]
            size = os.path.getsize(i)
            sec = os.path.getmtime(i)
            self.InsertStringItem(j, name)
            self.SetStringItem(j, 1, ex)
            self.SetStringItem(j, 2, str(size) + ' B')
            self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))
            self.SetItemImage(j, 1)
            j += 1

        # after append all files in directory
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files.sort()

        for i in files:
            (name, ext) = os.path.splitext(i)
            ex = ext[1:]
            size = os.path.getsize(i)
            sec = os.path.getmtime(i)
            self.InsertStringItem(j, name)
            self.SetStringItem(j, 1, ex)
            self.SetStringItem(j, 2, str(size) + ' B')
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