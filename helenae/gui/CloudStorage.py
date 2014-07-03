# -*- coding: utf-8 -*-
import wx
import wx.lib.agw.hyperlink as hl

from widgets.RegisterCtrl import RegisterWindow, ID_BUTTON_EXIT
from widgets.Filemanager import FileManager, ID_EXIT

ID_BUTTON_ACCEPT = 700
ID_BUTTON_CANCEL = 701
ID_TEXT_INPUT_LOG = 702
ID_TEXT_LABLE_LOG = 703
ID_TEXT_INPUT_PSW = 704
ID_TEXT_LABEL_PSW = 705
ID_NEW_MEMBER_TXT = 706


class CloudStorage(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # widgets
        self.RegisterWindow = RegisterWindow(self, -1, 'Создание аккаунта')
        self.FileManager = FileManager(self, -1, 'CloudStorage')

        # inputs
        self.login_label = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Логин', pos=(15, 15))
        self.login_input = wx.TextCtrl(self, ID_TEXT_INPUT_LOG, size=(210, -1), pos=(75, 10))
        self.pass_label = wx.StaticText(self, ID_TEXT_LABEL_PSW, label='Пароль', pos=(15, 45))
        self.pass_input = wx.TextCtrl(self, ID_TEXT_INPUT_PSW, size=(210, -1), pos=(75, 40), style=wx.TE_PASSWORD)

        # buttons
        self.accept_button = wx.Button(self, id=ID_BUTTON_ACCEPT, label='Войти', pos=(15, 75))
        self.accept_button.SetBackgroundColour('#BFD8DF')
        self.accept_button.SetForegroundColour("#2F4D57")
        self.accept_button.SetFont((wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.cancel_button = wx.Button(self, id=ID_BUTTON_CANCEL, label='Отмена', pos=(110, 75))

        # hyperlink to register
        self.new_member_label = hl.HyperLinkCtrl(self, ID_NEW_MEMBER_TXT, 'Зарегистрироваться...', pos=(15,110))
        self.new_member_label.EnableRollover(True)
        self.new_member_label.SetUnderlines(False, False, True)
        self.new_member_label.AutoBrowse(False)
        self.new_member_label.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))

        # events
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnRegisterNewUser, id=ID_NEW_MEMBER_TXT)
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_BUTTON_CANCEL)
        # events for Register window
        self.Bind(wx.EVT_BUTTON, self.OnExitRegister, id=ID_BUTTON_EXIT)
        # events for Filemanager window
        self.Bind(wx.EVT_BUTTON, self.OnLoginUser, id=ID_BUTTON_ACCEPT)
        self.Bind(wx.EVT_MENU, self.OnExitFilemanager, id=ID_EXIT) # exit thought menu
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT) # exit from button in ButtonBox

        # form settings
        size = (300, 135)
        self.SetSize(size)
        self.icon = wx.Icon('./gui/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.Show()

    def OnLoginUser(self, event):
        self.Hide()
        self.FileManager.Show()

    def OnExit(self, event):
        self.Close()
        self.RegisterWindow.Close()
        self.FileManager.Close()

    def OnRegisterNewUser(self, event):
        self.Hide()
        self.RegisterWindow.Show()

    def OnExitRegister(self, event):
        self.Close()
        self.RegisterWindow.Close()

    def OnExitFilemanager(self, event):
        self.Close()
        self.RegisterWindow.Close()
        self.FileManager.Close()


if __name__ =='__main__':
    app = wx.App(0)
    frame = CloudStorage(None, -1, 'Авторизация')
    frame.Show()
    app.MainLoop()