# -*- coding: utf-8 -*-
import os
import wx
from ValidatorMsgDlg import ValidatorMsgDialog


class FileValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.dlg = None

    def Clone(self):  # Required method for validator
        return FileValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8').strip()
        text = text.translate(None, "~|*:'><?!@#^&%=+`$[]{}," + '"')
        text = os.path.normpath(text)
        text = os.path.normcase(text)
        dirs, filename = os.path.split(text)
        dirs = dirs.replace('\\', '/')
        if dirs.startswith('/'):
            dirs = dirs[1:]
        if len(dirs) > 0 and len(dirs.split('/')) >= 1:
            text = os.path.normpath(dirs+"/"+filename)
        else:
            text = filename

        if len(text) < 2:
            self.dlg = ValidatorMsgDialog(None, "Это поле не может быть пустым!")
            self.dlg.Centre()
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