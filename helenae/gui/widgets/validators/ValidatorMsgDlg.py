# -*- coding: utf-8 -*-
import wx

import platform

ID_MSG_DLG_ICO = 1500
ID_MSG_DLG_LABEL = 1550

class ValidatorMsgDialog(wx.Dialog):
    def __init__(self, parent, msg):
        wx.Dialog.__init__(self, parent, -1, 'Сообщение')

        # Mac OS X
        if platform.system() == 'Darwin':
            DefaultTxtFontSize = 14
            ButtonPos = (200, 95)
        # Windows/Linux
        else:
            DefaultTxtFontSize = 10
            ButtonPos = (205, 115)

        wx.Button(self, wx.ID_OK, pos=ButtonPos)

        # lables, which contains some text
        words = msg.strip().split(' ')
        i=0
        string = ''
        for word in words:
            if len(string) < 40:
                string += word + ' '
            else:
                txt = wx.StaticText(self, id=1550, label=string, pos=(60, 25 + 15 * i))
                txt.SetFont(wx.Font(DefaultTxtFontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
                string = word + ' '
                i += 1
        else:
            txt = wx.StaticText(self, id=1550, label=string, pos=(60, 25 + 15 * i))
            txt.SetFont(wx.Font(DefaultTxtFontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
            string += word + ' '

        # form settings
        size = (300, 150)
        self.SetSize(size)


if __name__ == '__main__':
    app = wx.App(0)
    msg_dlg = ValidatorMsgDialog(None, "Копирование завершено!")
    msg_dlg.ShowModal()
    app.MainLoop()