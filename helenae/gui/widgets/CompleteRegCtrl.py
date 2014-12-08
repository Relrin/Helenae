# -*- coding: utf-8 -*-
import wx

import platform

ID_BUTTON_CLOSE_MSG = 1000
ID_LABLE_TEXT_INFO = 1001
ID_ICON_INFO = 1002


class CompleteRegCtrl(wx.Frame):

    def __init__(self, parent, id, title, ico_folder):

        if platform.system() == 'Darwin':
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            DefaultTxtSizeFont = 12
            DefaultPosButton = (215, 90)
        # Windows/Linux
        else:
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            DefaultTxtSizeFont = 10
            DefaultPosButton = (225, 115)

        # lables, which contains some text
        self.txt = wx.StaticText(self, id=ID_LABLE_TEXT_INFO, label="После перезапуска приложения Вы", pos=(60, 25))
        self.txt.SetFont(wx.Font(DefaultTxtSizeFont, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
        self.txt = wx.StaticText(self, id=ID_LABLE_TEXT_INFO, label="можете авторизироваться", pos=(85, 40))
        self.txt.SetFont(wx.Font(DefaultTxtSizeFont, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))

        # buttons
        self.cancel_button = wx.Button(self, id=ID_BUTTON_CLOSE_MSG, label='Закрыть', pos=DefaultPosButton)

        # form settings
        size = (320, 150)
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)


if __name__ =='__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = CompleteRegCtrl(None, -1, 'Сообщение', ico_folder)
    frame.Show()
    app.MainLoop()