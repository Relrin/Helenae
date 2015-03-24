# -*- coding: utf-8 -*-
import wx
import wx.animate
import wx.lib.agw.hyperlink as hl

from widgets.RegisterCtrl import RegisterWindow, ID_BUTTON_EXIT
from widgets.Filemanager import FileManager, ID_EXIT
from widgets.validators.LoginValidator import LoginValidator
from widgets.validators.PasswordValidator import PasswordValidator

import platform

ID_BUTTON_ACCEPT = 700
ID_BUTTON_CANCEL = 701
ID_TEXT_INPUT_LOG = 702
ID_TEXT_LABLE_LOG = 703
ID_TEXT_INPUT_PSW = 704
ID_TEXT_LABEL_PSW = 705
ID_NEW_MEMBER_TXT = 706
ID_ERROR_USER = 707
ID_ERROR_PSW = 708
ID_PRELOADER = 709


class CloudStorage(wx.Frame):

    def __init__(self, parent, id, title, ico_folder):

        # Mac OS X
        if platform.system() == 'Darwin':
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            DefaultButtonFontSize = 12
            DefaultErrorLabelFontSize = 9
            LinkFontSize = 10
            size = (310, 180)
        # Windows/Linux
        else:
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            DefaultButtonFontSize = 8
            DefaultErrorLabelFontSize = 7
            LinkFontSize = 8
            size = (310, 150)

        # widgets
        self.RegisterWindow = RegisterWindow(self, -1, 'Создание аккаунта', ico_folder)
        self.FileManager = FileManager(self, -1, 'Многопользовательское распределённое приложение организации файлового обмена', ico_folder)

        # inputs
        self.login_label = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Логин', pos=(15, 15))
        self.login_input = wx.TextCtrl(self, ID_TEXT_INPUT_LOG, wx.EmptyString, size=(210, -1), pos=(75, 10),
                                       validator = LoginValidator())
        self.pass_label = wx.StaticText(self, ID_TEXT_LABEL_PSW, label='Пароль', pos=(15, 55))
        self.pass_input = wx.TextCtrl(self, ID_TEXT_INPUT_PSW, wx.EmptyString, size=(210, -1), pos=(75, 50),
                                      style=wx.TE_PASSWORD, validator = PasswordValidator())

        # error labels
        self.error_login = wx.StaticText(self, ID_ERROR_USER, label='', pos=(75, 35))
        self.error_login.SetForegroundColour('#DE4421')
        self.error_login.SetFont((wx.Font(DefaultErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_psw = wx.StaticText(self, ID_ERROR_PSW, label='', pos=(75, 75))
        self.error_psw.SetForegroundColour('#DE4421')
        self.error_psw.SetFont((wx.Font(DefaultErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        # buttons
        self.accept_button = wx.Button(self, id=ID_BUTTON_ACCEPT, label='Войти', pos=(15, 95))
        self.accept_button.SetBackgroundColour('#BFD8DF')
        self.accept_button.SetForegroundColour("#2F4D57")
        self.accept_button.SetFont((wx.Font(DefaultButtonFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.cancel_button = wx.Button(self, id=ID_BUTTON_CANCEL, label='Отмена', pos=(110, 95))

        # hyperlink to register
        self.new_member_label = hl.HyperLinkCtrl(self, ID_NEW_MEMBER_TXT, 'Зарегистрироваться...', pos=(15,130))
        self.new_member_label.EnableRollover(True)
        self.new_member_label.SetUnderlines(False, False, True)
        self.new_member_label.AutoBrowse(False)
        self.new_member_label.SetFont(wx.Font(LinkFontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))

        # preloader
        self.preloader = wx.animate.AnimationCtrl(self, ID_PRELOADER, pos=(260, 97), size=(24, 24))
        self.preloader.LoadFile(ico_folder + '/icons/preloader.gif', wx.animate.ANIMATION_TYPE_GIF)
        self.preloader.Hide()

        # events
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnRegisterNewUser, id=ID_NEW_MEMBER_TXT)
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_BUTTON_CANCEL)
        # events for Register window
        self.Bind(wx.EVT_BUTTON, self.OnExitRegister, id=ID_BUTTON_EXIT)
        # events for Filemanager window
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)  # exit through menu
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)  # exit from button in ButtonBox

        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.Center()
        self.Show()

    def PreloaderPlay(self):
        self.preloader.Show()
        self.preloader.Play()

    def PreloaderStop(self):
        self.preloader.Hide()
        self.preloader.Stop()

    def ShowErrorLogin(self, error_msg):
        self.error_login.SetLabel(error_msg)

    def ShowErrorPassword(self, error_msg):
        self.error_psw.SetLabel(error_msg)

    def ClearErrorsLabels(self):
        self.error_login.SetLabel('')
        self.error_psw.SetLabel('')

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


if __name__ =='__main__':
    app = wx.App(0)
    ico_folder = '.'
    frame = CloudStorage(None, -1, 'Авторизация', ico_folder)
    frame.Show()
    app.MainLoop()
