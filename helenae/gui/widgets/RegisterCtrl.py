# -*- coding: utf-8 -*-
import wx

ID_BUTTON_ACCEPT = 800
ID_BUTTON_EXIT = 801
ID_TEXT_INPUT_LOG = 802
ID_TEXT_LABLE_LOG = 803
ID_TEXT_INPUT_PSW = 804
ID_TEXT_LABEL_PSW = 805
ID_TEXT_INPUT_FULLNAME = 806
ID_TEXT_LABLE_FULLNAME = 807
ID_TEXT_INPUT_EMAIL = 808
ID_TEXT_LABLE_EMAIL = 809
ID_ERROR_L1_LOGIN = 810
ID_ERROR_M1_LOGIN = 811
ID_ERROR_L2_PSW = 812
ID_ERROR_M2_PSW = 813
ID_ERROR_L3_NAME = 814
ID_ERROR_M3_NAME = 815
ID_ERROR_L4_EMAIL = 816
ID_ERROR_M4_EMAIL = 817

class RegisterWindow(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # info label
        self.new_user = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Регистрация нового пользователя', pos=(35, 15))
        self.new_user.SetForegroundColour('#77899A')
        self.new_user.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        # error lables
        self.error_l1_login = wx.StaticText(self, ID_ERROR_L1_LOGIN, label='', pos=(115, 75))
        self.error_m1_login = wx.StaticText(self, ID_ERROR_M1_LOGIN, label='', pos=(330, 55))
        self.error_l1_login.SetForegroundColour('#DE4421')
        self.error_m1_login.SetForegroundColour('#DE4421')
        self.error_l1_login.SetFont((wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.error_m1_login.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_l2_login = wx.StaticText(self, ID_ERROR_L2_PSW, label='', pos=(115, 115))
        self.error_m2_login = wx.StaticText(self, ID_ERROR_M2_PSW, label='', pos=(330, 95))
        self.error_l2_login.SetForegroundColour('#DE4421')
        self.error_m2_login.SetForegroundColour('#DE4421')
        self.error_l2_login.SetFont((wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.error_m2_login.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_l3_login = wx.StaticText(self, ID_ERROR_L3_NAME, label='', pos=(115, 155))
        self.error_m3_login = wx.StaticText(self, ID_ERROR_M3_NAME, label='', pos=(330, 135))
        self.error_l3_login.SetForegroundColour('#DE4421')
        self.error_m3_login.SetForegroundColour('#DE4421')
        self.error_l3_login.SetFont((wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.error_m3_login.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.error_l4_login = wx.StaticText(self, ID_ERROR_L4_EMAIL, label='', pos=(115, 195))
        self.error_m4_login = wx.StaticText(self, ID_ERROR_M4_EMAIL, label='', pos=(330, 175))
        self.error_l4_login.SetForegroundColour('#DE4421')
        self.error_m4_login.SetForegroundColour('#DE4421')
        self.error_l4_login.SetFont((wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.error_m4_login.SetFont((wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        # inputs
        self.login_label = wx.StaticText(self, ID_TEXT_LABLE_LOG, label='Логин', pos=(60, 55))
        self.login_input = wx.TextCtrl(self, ID_TEXT_INPUT_LOG, size=(210, -1), pos=(115, 50))
        self.pass_label = wx.StaticText(self, ID_TEXT_LABEL_PSW, label='Пароль', pos=(60, 95))
        self.pass_input = wx.TextCtrl(self, ID_TEXT_INPUT_PSW, size=(210, -1), pos=(115, 90), style=wx.TE_PASSWORD)
        self.fullname_label = wx.StaticText(self, ID_TEXT_LABLE_FULLNAME, label='Ф.И.О.', pos=(60, 135))
        self.fullname_input = wx.TextCtrl(self, ID_TEXT_INPUT_FULLNAME, size=(210, -1), pos=(115, 130))
        self.email_label = wx.StaticText(self, ID_TEXT_LABLE_EMAIL, label='E-mail', pos=(60, 175))
        self.email_input = wx.TextCtrl(self, ID_TEXT_INPUT_EMAIL, size=(210, -1), pos=(115, 170))

        # buttons
        self.accept_button = wx.Button(self, id=ID_BUTTON_ACCEPT, label='Отправить', pos=(110, 225))
        self.accept_button.SetBackgroundColour('#BFD8DF')
        self.accept_button.SetForegroundColour("#2F4D57")
        self.accept_button.SetFont((wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))
        self.cancel_button = wx.Button(self, id=ID_BUTTON_EXIT, label='Выйти', pos=(205, 225))

        # form settings
        size = (400, 270)
        self.SetSize(size)
        self.icon = wx.Icon('./gui/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

    def ShowErrorLogin(self, error_msg):
        self.error_l1_login.SetLabel(error_msg)
        self.error_m1_login.SetLabel('*')

    def ShowErrorPassword(self, error_msg):
        self.error_l2_login.SetLabel(error_msg)
        self.error_m2_login.SetLabel('*')

    def ShowErrorName(self, error_msg):
        self.error_l3_login.SetLabel(error_msg)
        self.error_m3_login.SetLabel('*')

    def ShowErrorEmail(self, error_msg):
        self.error_l4_login.SetLabel(error_msg)
        self.error_m4_login.SetLabel('*')

    def ClearErrorsLabels(self):
        self.error_l1_login.SetLabel('')
        self.error_m1_login.SetLabel('')
        self.error_l2_login.SetLabel('')
        self.error_m2_login.SetLabel('')
        self.error_l3_login.SetLabel('')
        self.error_m3_login.SetLabel('')
        self.error_l4_login.SetLabel('')
        self.error_m4_login.SetLabel('')

    def OnExit(self, event):
        self.Close()

if __name__ =='__main__':
    app = wx.App(0)
    frame = RegisterWindow(None, -1, 'Создание аккаунта')
    frame.Show()
    app.MainLoop()