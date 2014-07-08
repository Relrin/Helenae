# -*- coding: utf-8 -*-
import wx
import wx.lib.agw.hyperlink as hl

ID_BUTTON_CLOSE = 900
ID_LINK_SITE = 901
ID_ABOUT_ICONS = 903
ID_ABOUT_RIGHTS = 904
ID_ABOUT_TXT = 905
ID_ABOUT_MAIN = 906


class About(wx.Frame):

    def __init__(self, parent, id, title, ico_folder):
        wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # lables, which contains some text
        txt = """Распределенное файловое хранилище"""
        self.about_txt = wx.StaticText(self, id=ID_ABOUT_MAIN, label=txt, pos=(25,15))
        self.about_txt.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0))

        about = """Дипломный проект по специальности \n             инженер-программист"""
        self.icons_txt = wx.StaticText(self, id=ID_ABOUT_TXT, label=about, pos=(15, 55))
        self.icons_txt.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))

        icons = """Иконки предоставлены http://www.fatcow.com/ \nпо лицензии Creative Commons Attribution 3.0"""
        self.icons_txt = wx.StaticText(self, id=ID_ABOUT_ICONS, label=icons, pos=(15, 105))

        rights = """© Copyright 2014-2015, Савич Валерий"""
        self.rights_txt = wx.StaticText(self, id=ID_ABOUT_RIGHTS, label=rights, pos=(30, 140))

        # buttons
        self.cancel_button = wx.Button(self, id=ID_BUTTON_CLOSE, label='Закрыть', pos=(205, 165))

        # hyperlink to site
        self.new_member_label = hl.HyperLinkCtrl(self, ID_LINK_SITE, "Перейти на сайт", pos=(15, 175), URL="https://127.0.0.1:8080/")
        self.new_member_label.EnableRollover(True)
        self.new_member_label.SetUnderlines(False, False, True)
        self.new_member_label.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))

        # events
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_BUTTON_CLOSE)

        # form settings
        size = (300, 200)
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

    def OnExit(self, event):
        self.Close()

if __name__ =='__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = About(None, -1, 'О программе', ico_folder)
    frame.Show()
    app.MainLoop()