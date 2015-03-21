# -*- coding: utf-8 -*-
import wx
import platform


class InputDialog(wx.Dialog):
    def __init__(self, parent, id, title, ico_folder, validator, field_text='', lable_name='Имя элемента'):

        if platform.system() == 'Darwin':
            wx.Dialog.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            labelPos = (15, 15)
            fieldSize = (125, 20)
            fieldPos = (130, 15)
            size = (275, 105)
        else:
            wx.Dialog.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            labelPos = (15, 20)
            fieldSize = (140, 20)
            fieldPos = (115, 15)
            size = (275, 80)

        self.label = wx.StaticText(self, label=lable_name + ":", pos=labelPos)
        self.field = wx.TextCtrl(self, value="", size=fieldSize, pos=fieldPos, validator=validator)
        self.button_ok = wx.Button(self, label="Ок", id=wx.ID_OK, pos=(75, 45))
        self.button_cancel = wx.Button(self, label="Отмена", id=wx.ID_CANCEL, pos=(167, 45))

        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)

        # self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        # self.SetIcon(self.icon)
        self.SetSize(size)
        self.field.SetValue(field_text)
        self.result = None
        self.Center()

    def onOK(self, event):
        if self.field.GetValidator().Validate(self.field):
            self.result = self.field.GetValue()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def onCancel(self, event):
        self.result = None
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()


if __name__ =='__main__':
    from validators.FileValidator import FileValidator
    app = wx.App(0)
    ico_folder = '..'
    frame = InputDialog(None, -1, 'Ввод данных', ico_folder, FileValidator())
    res = frame.ShowModal()
    app.MainLoop()
