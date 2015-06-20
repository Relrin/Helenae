# -*- coding: utf-8 -*-
import wx
import platform


class InputLink(wx.Dialog):
    def __init__(self, parent, id, title, ico_folder):

        if platform.system() == 'Darwin':
            wx.Dialog.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            labelPos = (10, 15)
            fieldSize = (180, 20)
            fieldPos = (125, 15)
            size = (320, 105)
        else:
            wx.Dialog.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            labelPos = (10, 20)
            fieldSize = (195, 20)
            fieldPos = (110, 15)
            size = (320, 80)

        self.label = wx.StaticText(self, label="Link on the file:", pos=labelPos)
        self.field = wx.TextCtrl(self, value="", size=fieldSize, pos=fieldPos)
        self.button_ok = wx.Button(self, label="Ok", id=wx.ID_OK, pos=(125, 45))
        self.button_cancel = wx.Button(self, label="Cancel", id=wx.ID_CANCEL, pos=(217, 45))

        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)

        # self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        # self.SetIcon(self.icon)
        self.SetSize(size)
        self.result = None
        self.Center()

    def onOK(self, event):
        self.result = self.field.GetValue()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onCancel(self, event):
        self.result = None
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()


if __name__ =='__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = InputLink(None, -1, 'Enter shared link', ico_folder)
    res = frame.ShowModal()
    app.MainLoop()
