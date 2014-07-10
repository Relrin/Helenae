# -*- coding: utf-8 -*-
import os
import wx
import sys
import ntpath

from FileListCtrl import FileListCtrl
from OptionsCtrl import OptionsCtrl
from InputDialogCtrl import InputDialog
from validators.FolderValidator import FolderValidator
from validators.FileValidator import FileValidator

ID_BUTTON = 100
ID_BUTTON_WRITE = 101
ID_BUTTON_SYNC = 102
ID_BUTTON_TRANSFER = 103
ID_BUTTON_CREATE_FOLDER = 104
ID_BUTTON_REMOVE_FILE = 105
ID_BUTTON_RENAME = 106
ID_NEW = 150
ID_FOLDER = 151
ID_RENAME = 152
ID_REPLACE = 153
ID_REMOVE = 154
ID_SYNC = 155
ID_SHOW_STATUSBAR = 156
ID_OPTIONS = 157
ID_WRITE = 158
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
        self.parent = parent
        self.ico_folder = ico_folder

        # file frame
        self.files_folder = FileListCtrl(self, -1, ico_folder)
        # options frame
        self.options_frame = OptionsCtrl(self, -1, "Опции", ico_folder)

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
        writeItem = wx.MenuItem(filemenu, ID_WRITE, "&Запись", help='Записать выделенные файлы')
        writeItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/write.png'))
        deleteItem = wx.MenuItem(filemenu, ID_REMOVE, "&Удалить", help='Удалить выделенные файлы')
        deleteItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/delete.png'))
        syncItem = wx.MenuItem(filemenu, ID_SYNC, "&Синхронизация", help='Синхронизировать выделенные файлы')
        syncItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/sync.png'))
        filemenu.AppendItem(newItem)
        filemenu.AppendItem(createItem)
        filemenu.AppendSeparator()
        filemenu.AppendItem(renameItem)
        filemenu.AppendItem(removeItem)
        filemenu.AppendItem(writeItem)
        filemenu.AppendItem(deleteItem)
        filemenu.AppendItem(syncItem)
        filemenu.AppendSeparator()
        exitItem = wx.MenuItem(filemenu, ID_EXIT, "&Выход", help='Выход из приложения')
        exitItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/exit.png'))
        filemenu.AppendItem(exitItem)

        configmenu = wx.Menu()
        self.show_statusbar = configmenu.Append(ID_SHOW_STATUSBAR, 'Отображать статусбар', 'Отображать статусбар', kind=wx.ITEM_CHECK)
        configmenu.Check(self.show_statusbar.GetId(), True)
        self.preferencesItem = wx.MenuItem(filemenu, ID_OPTIONS, "&Параметры", help='Основные параметры приложения')
        self.preferencesItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/preferences/preferences.png'))
        configmenu.AppendItem(self.preferencesItem)

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

        button1 = wx.Button(self, ID_BUTTON_WRITE, "F4 Запись")
        button1.SetBackgroundColour('#BFD8DF')
        button1.SetForegroundColour("#2F4D57")

        button2 = wx.Button(self, ID_BUTTON_SYNC, "F5 Синхр.")
        button2.SetBackgroundColour('#BFD8DF')
        button2.SetForegroundColour("#2F4D57")

        button3 = wx.Button(self, ID_BUTTON_TRANSFER, "F6 Перенос")
        button3.SetBackgroundColour('#BFD8DF')
        button3.SetForegroundColour("#2F4D57")

        button4 = wx.Button(self, ID_BUTTON_CREATE_FOLDER, "F7 Созд. каталог")
        button4.SetBackgroundColour('#BFD8DF')
        button4.SetForegroundColour("#2F4D57")

        button5 = wx.Button(self, ID_BUTTON_REMOVE_FILE, "F8 Удалить")
        button5.SetBackgroundColour('#BFD8DF')
        button5.SetForegroundColour("#2F4D57")

        button6 = wx.Button(self, ID_BUTTON_RENAME, "F9 Перемеин.")
        button6.SetBackgroundColour('#BFD8DF')
        button6.SetForegroundColour("#2F4D57")

        button7 = wx.Button(self, ID_EXIT, "F10 Выход")
        button7.SetBackgroundColour('#BFD8DF')
        button7.SetForegroundColour("#2F4D57")

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
        self.Bind(wx.EVT_MENU, self.ShowMenu, self.preferencesItem)
        self.Bind(wx.EVT_CLOSE, self.OnExitProgramm)
        # create folder
        self.Bind(wx.EVT_BUTTON, self.OnCreateFolder, id=ID_BUTTON_CREATE_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnCreateFolder, id=ID_FOLDER)
        # create file
        self.Bind(wx.EVT_MENU, self.OnCreateFile, id=ID_NEW)

        # define size and icon for app
        size = (800, 600)
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize(size)

        # add status bar
        self.sb = self.CreateStatusBar()
        self.Center()

    def OnCreateFolder(self, event):
        dlg = InputDialog(self, -1, 'Введите каталог', self.ico_folder, FolderValidator())
        dlg.ShowModal()
        if dlg.result is not None:
            try:
                new_folder = self.files_folder.currentDir + dlg.result
                os.makedirs(new_folder)
            except OSError:
                wx.MessageBox("Вероятнее всего, такой файл или каталог уже существует!\nПожалуйста, дайте файлу другое имя.", 'Ошибка')
            except Exception, exc:
                wx.MessageBox("%s" % exc.message, "Ошибка")
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)

    def OnCreateFile(self, event):
        dlg = InputDialog(self, -1, 'Введите имя файла и расширение', self.ico_folder, FileValidator())
        dlg.ShowModal()
        if dlg.result is not None:
            try:
                new_file = self.files_folder.currentDir + dlg.result
                new_folders, filename = ntpath.split(dlg.result)
                if len(new_folders) > 2:
                    os.makedirs(self.files_folder.currentDir + new_folders)
                open(new_file, 'a').close()
            except OSError:
                wx.MessageBox("Вероятнее всего, такой файл или каталог уже существует!\nПожалуйста, дайте файлу другое имя.", 'Ошибка')
            except Exception, exc:
                wx.MessageBox("%s" % exc.message, "Ошибка")
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)

    def ShowMenu(self, event):
        self.options_frame.Show()

    def ToggleStatusBar(self, event):
        if self.show_statusbar.IsChecked():
            self.sb.Show()
        else:
            self.sb.Hide()

    def OnExit(self, event):
        self.Close()

    def OnExitProgramm(self, event):
        self.parent.Close()

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