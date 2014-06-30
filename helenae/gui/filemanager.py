# -*- coding: utf-8 -*-

import wx
import os

from widgets.FileListCtrl import FileListCtrl


ID_BUTTON = 100
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

class CloudStorage(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title)

        # file frame
        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(50)

        p1 = FileListCtrl(self.splitter, -1)
        p2 = FileListCtrl(self.splitter, -1)
        self.splitter.SplitVertically(p1, p2)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.OnDoubleClick, id=ID_SPLITTER)

        # menu
        filemenu= wx.Menu()
        filemenu.Append(ID_EXIT, "&Выход", "Выход из программы")
        editmenu = wx.Menu()
        configmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&Файл")
        menuBar.Append(editmenu, "&Редактирование")
        menuBar.Append(configmenu, "&Настройка")
        menuBar.Append(helpmenu, "&Помощь")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)

        # toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        tb.AddSimpleTool(10, wx.Bitmap('./gui/icons/ui/toolbar/previous.png'), 'Previous')
        tb.AddSimpleTool(20, wx.Bitmap('./gui/icons/ui/toolbar/up.png'), 'Up one directory')
        tb.AddSimpleTool(30, wx.Bitmap('./gui/icons/ui/toolbar/home.png'), 'Home')
        tb.AddSimpleTool(40, wx.Bitmap('./gui/icons/ui/toolbar/refresh.png'), 'Refresh')
        tb.AddSeparator()
        tb.AddSimpleTool(60, wx.Bitmap('./gui/icons/ui/toolbar/terminal.png'), 'Terminal')
        tb.AddSeparator()
        tb.AddSimpleTool(70, wx.Bitmap('./gui/icons/ui/toolbar/help.png'), 'Help')
        tb.Realize()

        # button panel
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        button1 = wx.Button(self, ID_BUTTON + 1, "F3 View")
        button2 = wx.Button(self, ID_BUTTON + 2, "F4 Edit")
        button3 = wx.Button(self, ID_BUTTON + 3, "F5 Copy")
        button4 = wx.Button(self, ID_BUTTON + 4, "F6 Move")
        button5 = wx.Button(self, ID_BUTTON + 5, "F7 Mkdir")
        button6 = wx.Button(self, ID_BUTTON + 6, "F8 Delete")
        button7 = wx.Button(self, ID_BUTTON + 7, "F9 Rename")
        button8 = wx.Button(self, ID_EXIT, "F10 Quit")

        self.sizer2.Add(button1, 1, wx.EXPAND)
        self.sizer2.Add(button2, 1, wx.EXPAND)
        self.sizer2.Add(button3, 1, wx.EXPAND)
        self.sizer2.Add(button4, 1, wx.EXPAND)
        self.sizer2.Add(button5, 1, wx.EXPAND)
        self.sizer2.Add(button6, 1, wx.EXPAND)
        self.sizer2.Add(button7, 1, wx.EXPAND)
        self.sizer2.Add(button8, 1, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter,1,wx.EXPAND)
        self.sizer.Add(self.sizer2,0,wx.EXPAND)
        self.SetSizer(self.sizer)

        # define size and icon for app
        size = (800, 600)
        self.SetSize(size)
        self.icon = wx.Icon('./gui/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        # add status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(os.getcwd())
        self.Center()

    def OnExit(self,e):
        self.Close(True)

    def OnSize(self, event):
        size = self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)
        self.sb.SetStatusText(os.getcwd())
        event.Skip()

    def OnDoubleClick(self, event):
        size =  self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)

if __name__ == '__main__':
    app = wx.App(0)
    frame = CloudStorage(None, -1, 'CloudStorage')
    frame.Show(True)
    app.MainLoop()