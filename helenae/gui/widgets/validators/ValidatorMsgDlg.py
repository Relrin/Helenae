# -*- coding: utf-8 -*-
import wx

ID_MSG_DLG_ICO = 1500
ID_MSG_DLG_LABEL = 1550

class ValidatorMsgDialog(wx.Dialog):
    def __init__(self, parent, msg):
        wx.Dialog.__init__(self, parent, -1, 'Сообщение')
        wx.Button(self, wx.ID_OK, pos=(205, 115))

        # lables, which contains some text
        words = msg.strip().split(' ')
        i=0
        string = ''
        for word in words:
            if len(string) < 40:
                string += word + ' '
            else:
                txt = wx.StaticText(self, id=1550, label=string, pos=(60, 25 + 15 * i))
                txt.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
                string = word + ' '
                i += 1
        else:
            txt = wx.StaticText(self, id=1550, label=string, pos=(60, 25 + 15 * i))
            txt.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
            string += word + ' '

        # form settings
        size = (300, 150)
        self.SetSize(size)