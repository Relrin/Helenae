# -*- coding: utf-8 -*-
import os
import wx
import ntpath
from ValidatorMsgDlg import ValidatorMsgDialog


class FileValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.dlg = None

    def Clone(self):  # Required method for validator
        return FileValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8').strip()
        text = text.translate(None, "~|*:'><?!@#^&%=+`$[]{}," + '"')
        text = os.path.normpath(text)
        text = os.path.normcase(text)
        dirs, filename = ntpath.split(text)
        text = os.path.normpath(dirs.replace('\\', '/')+"//"+filename)

        if len(text) < 3:
            self.dlg = ValidatorMsgDialog(None, "Это поле не может быть пустым!")
            self.dlg.ShowModal()
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetValue(text)
            textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True