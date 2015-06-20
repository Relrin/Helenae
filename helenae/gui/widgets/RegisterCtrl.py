# -*- coding: utf-8 -*-
import wx
import wx.animate

from validators.LoginValidator import LoginValidator
from validators.PasswordValidator import PasswordValidator
from validators.NameValidator import NameValidator

from CompleteRegCtrl import CompleteRegCtrl

import platform

ID_BUTTON_REG = 800
ID_BUTTON_EXIT = 801
ID_TEXT_INPUT_LOG = 802
ID_TEXT_LABLE_LOG = 803
ID_TEXT_INPUT_PSW = 804
ID_TEXT_LABEL_PSW = 805
ID_TEXT_INPUT_FULLNAME = 806
ID_TEXT_LABLE_FULLNAME = 807
ID_TEXT_INPUT_EMAIL = 808
ID_TEXT_LABLE_EMAIL = 809
ID_ERROR_LOGIN = 810
ID_ERROR_PSW = 812
ID_ERROR_NAME = 814
ID_ERROR_EMAIL = 816
ID_PRELOADER_REGISTER = 817


class RegisterWindow(wx.Frame):

    def __init__(self, parent, id, title, ico_folder):

        if platform.system() == 'Darwin':
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            RegisterLabelPos = (145, 15)
            ErrorLabelFontSize = 10
            SendButtonFontSize = 12
            size = (400, 290)
        else:
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            RegisterLabelPos = (35, 15)
            ErrorLabelFontSize = 7
            SendButtonFontSize = 8
            size = (400, 270)

        self.parent = parent

        self.msg_box = CompleteRegCtrl(self, -1, 'Message', ico_folder)
        # info label
        self.new_user = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Register new user', pos=RegisterLabelPos)
        self.new_user.SetForegroundColour('#77899A')
        self.new_user.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        # error lables
        self.error_login = wx.StaticText(self, ID_ERROR_LOGIN, label='', pos=(135, 75))
        self.error_login.SetForegroundColour('#DE4421')
        self.error_login.SetFont((wx.Font(ErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_psw = wx.StaticText(self, ID_ERROR_PSW, label='', pos=(135, 115))
        self.error_psw.SetForegroundColour('#DE4421')
        self.error_psw.SetFont((wx.Font(ErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_name = wx.StaticText(self, ID_ERROR_NAME, label='', pos=(135, 155))
        self.error_name.SetForegroundColour('#DE4421')
        self.error_name.SetFont((wx.Font(ErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_email = wx.StaticText(self, ID_ERROR_EMAIL, label='', pos=(135, 195))
        self.error_email.SetForegroundColour('#DE4421')
        self.error_email.SetFont((wx.Font(ErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        # inputs
        self.login_label = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Login', pos=(60, 55))
        self.login_input = wx.TextCtrl(self, ID_TEXT_INPUT_LOG, size=(210, -1), pos=(135, 50),
                                       validator=LoginValidator())
        self.pass_label = wx.StaticText(self, ID_TEXT_LABEL_PSW, label='Password', pos=(60, 95))
        self.pass_input = wx.TextCtrl(self, ID_TEXT_INPUT_PSW, size=(210, -1), pos=(135, 90), style=wx.TE_PASSWORD,
                                      validator=PasswordValidator())
        self.fullname_label = wx.StaticText(self, ID_TEXT_LABLE_FULLNAME, label='Fullname', pos=(60, 135))
        self.fullname_input = wx.TextCtrl(self, ID_TEXT_INPUT_FULLNAME, size=(210, -1), pos=(135, 130),
                                          validator=NameValidator())
        self.email_label = wx.StaticText(self, ID_TEXT_LABLE_EMAIL, label='E-mail', pos=(60, 175))
        self.email_input = wx.TextCtrl(self, ID_TEXT_INPUT_EMAIL, size=(210, -1), pos=(135, 170))

        # buttons
        self.accept_button = wx.Button(self, id=ID_BUTTON_REG, label='Send', pos=(110, 225))
        self.accept_button.SetBackgroundColour('#BFD8DF')
        self.accept_button.SetForegroundColour("#2F4D57")
        self.accept_button.SetFont((wx.Font(SendButtonFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.cancel_button = wx.Button(self, id=ID_BUTTON_EXIT, label='Exit', pos=(205, 225))

        # preloader
        self.preloader = wx.animate.AnimationCtrl(self, ID_PRELOADER_REGISTER, pos=(300, 228), size=(24, 24))
        self.preloader.LoadFile(ico_folder + '/icons/preloader.gif', wx.animate.ANIMATION_TYPE_GIF)
        self.preloader.Hide()

        # form settings
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder+'/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.Center()
        self.SetIcon(self.icon)

        self.Bind(wx.EVT_CLOSE, self.OnHide)

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

    def ShowErrorName(self, error_msg):
        self.error_name.SetLabel(error_msg)

    def ShowErrorEmail(self, error_msg):
        self.error_email.SetLabel(error_msg)

    def ClearErrorsLabels(self):
        self.error_login.SetLabel('')
        self.error_psw.SetLabel('')
        self.error_name.SetLabel('')
        self.error_email.SetLabel('')

    def OnHide(self, event):
        self.Hide()
        self.parent.Close()

    def OnExit(self, event):
        self.Close()

if __name__ =='__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = RegisterWindow(None, -1, 'Creating account', ico_folder)
    frame.Show()
    app.MainLoop()