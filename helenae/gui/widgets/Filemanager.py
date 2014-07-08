# -*- coding: utf-8 -*-
import os
import wx

from FileListCtrl import FileListCtrl


ID_BUTTON = 100
ID_NEW = 150
ID_FOLDER = 151
ID_RENAME = 152
ID_REPLACE = 153
ID_REMOVE = 154
ID_SYNC = 155
ID_SHOW_STATUSBAR = 156
ID_EXIT = 200
ID_SPLITTER = 300

# TODO: add into 'about' link to http://www.fatcow.com/ for icon theme
# TODO: add 'login/register' widget
# TODO: add 'options' widget
# TODO: add handlers for buttons/menus/etc.
# TODO: add icons for elements (buttons/menus/etc.)
# TODO: add logger
# TODO: save JSON configs in temp folder
# TODO: save part info (about catalog structure) in XML


class FileManager(wx.Frame):
    def __init__(self, parent, id, title, ico_folder):
        wx.Frame.__init__(self, parent, -1, title)

        # file frame
        self.files_folder = FileListCtrl(self, -1, ico_folder)

        # menu
        filemenu= wx.Menu()
        newItem = wx.MenuItem(filemenu, ID_NEW, "&Новый файл", help='Создать новый файл в каталоге')
        newItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/new.png'))
        createItem = wx.MenuItem(filemenu, ID_FOLDER, "&Создать каталог", help='Создать новый каталог')
        createItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/folder.png'))
        renameItem = wx.MenuItem(filemenu, ID_RENAME, "&Перемеиновать", help='Перемеиновать выделенный файл')
        renameItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/rename.png'))
        removeItem = wx.MenuItem(filemenu, ID_REPLACE, "&Перенос", help='Перенести выделенные файлы в другой каталог')
        removeItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/remove.png'))
        deleteItem = wx.MenuItem(filemenu, ID_REMOVE, "&Удалить", help='Удалить выделенные файлы')
        deleteItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/delete.png'))
        syncItem = wx.MenuItem(filemenu, ID_SYNC, "&Синхронизация", help='Синхронизировать выделенные файлы')
        syncItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/sync.png'))
        filemenu.AppendItem(newItem)
        filemenu.AppendItem(createItem)
        filemenu.AppendItem(renameItem)
        filemenu.AppendItem(removeItem)
        filemenu.AppendItem(deleteItem)
        filemenu.AppendItem(syncItem)
        filemenu.AppendSeparator()
        exitItem = wx.MenuItem(filemenu, ID_EXIT, "&Выход", help='Выход из приложения')
        exitItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/exit.png'))
        filemenu.AppendItem(exitItem)

        configmenu = wx.Menu()
        self.show_statusbar = configmenu.Append(ID_SHOW_STATUSBAR, 'Отображать статусбар', 'Отображать статусбар', kind=wx.ITEM_CHECK)
        configmenu.Check(self.show_statusbar.GetId(), True)
        preferencesItem = wx.MenuItem(filemenu, ID_EXIT, "&Параметры", help='Основные параметры приложения')
        preferencesItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/preferences/preferences.png'))
        configmenu.AppendItem(preferencesItem)

        about = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&Файл")
        menuBar.Append(configmenu, "&Настройки")
        menuBar.Append(helpmenu, "&Помощь")
        menuBar.Append(about, "&О программе")
        self.SetMenuBar(menuBar)

        # toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        tb.AddSimpleTool(10, wx.Bitmap(ico_folder + '/icons/ui/toolbar/previous.png'), 'Previous')
        tb.AddSimpleTool(20, wx.Bitmap(ico_folder + '/icons/ui/toolbar/up.png'), 'Up one directory')
        tb.AddSimpleTool(30, wx.Bitmap(ico_folder + '/icons/ui/toolbar/home.png'), 'Home')
        tb.AddSimpleTool(40, wx.Bitmap(ico_folder + '/icons/ui/toolbar/refresh.png'), 'Refresh')
        tb.AddSeparator()
        tb.AddSimpleTool(60, wx.Bitmap(ico_folder + '/icons/ui/toolbar/terminal.png'), 'Terminal')
        tb.AddSeparator()
        tb.AddSimpleTool(70, wx.Bitmap(ico_folder + '/icons/ui/toolbar/help.png'), 'Help')
        tb.Realize()

        # button panel
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        button1 = wx.Button(self, ID_BUTTON + 1, "F4 Запись")
        button2 = wx.Button(self, ID_BUTTON + 3, "F5 Синхр.")
        button3 = wx.Button(self, ID_BUTTON + 4, "F6 Перенести")
        button4 = wx.Button(self, ID_BUTTON + 5, "F7 Созд. каталог")
        button5 = wx.Button(self, ID_BUTTON + 6, "F8 Удалить")
        button6 = wx.Button(self, ID_BUTTON + 7, "F9 Перемеин.")
        button7 = wx.Button(self, ID_EXIT, "F10 Выход")

        self.sizer2.Add(button1, 1, wx.EXPAND)
        self.sizer2.Add(button2, 1, wx.EXPAND)
        self.sizer2.Add(button3, 1, wx.EXPAND)
        self.sizer2.Add(button4, 1, wx.EXPAND)
        self.sizer2.Add(button5, 1, wx.EXPAND)
        self.sizer2.Add(button6, 1, wx.EXPAND)
        self.sizer2.Add(button7, 1, wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.files_folder, 1,wx.EXPAND)
        self.sizer.Add(self.sizer2, 0,wx.EXPAND)
        self.SetSizer(self.sizer)

        # events bindings
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, self.show_statusbar)

        # define size and icon for app
        size = (800, 600)
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize(size)

        # add status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(os.getcwd())
        self.Center()

    def ToggleStatusBar(self, event):
        if self.show_statusbar.IsChecked():
            self.sb.Show()
        else:
            self.sb.Hide()

    def OnExit(self, event):
        self.Close()

    def OnSize(self, event):
        size = self.GetSize()
        self.files_folder.ResizeColumns(size.x)
        self.sb.SetStatusText(os.getcwd())
        event.Skip()

if __name__ == '__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = FileManager(None, -1, 'CloudStorage', ico_folder)
    frame.Show(True)
    app.MainLoop()