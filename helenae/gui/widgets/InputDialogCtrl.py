# -*- coding: utf-8 -*-
import wx


class InputDialog(wx.Dialog):
    def __init__(self, parent, id, title, ico_folder, validator):
        wx.Dialog.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.label = wx.StaticText(self, label="Имя элемента:", pos=(15, 20))
        self.field = wx.TextCtrl(self, value="", size=(150, 20), pos=(105, 15), validator=validator)
        self.button_ok = wx.Button(self, label="Ок", id=wx.ID_OK, pos=(75, 45))
        self.button_cancel = wx.Button(self, label="Отмена", id=wx.ID_CANCEL, pos=(167, 45))

        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)

        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        size = (275, 80)
        self.SetSize(size)
        self.result = None

    def onOK(self, event):
        if self.field.GetValidator().Validate(self.field):
            self.result = self.field.GetValue()
        self.Destroy()

    def onCancel(self, event):
        self.result = None
        self.Destroy()

if __name__ =='__main__':
    from validators.FileValidator import FileValidator
    app = wx.App(0)
    ico_folder = '..'
    frame = InputDialog(None, -1, 'Ввод данных', ico_folder, FileValidator())
    frame.Show()
    app.MainLoop()

