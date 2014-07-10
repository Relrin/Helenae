# -*- coding: utf-8 -*-
import wx
from ValidatorMsgDlg import ValidatorMsgDialog


class LoginValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.dlg = None

    def Clone(self):  # Required method for validator
        return LoginValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8').strip().replace(' ', '')
        text = text.translate(None, "~|*:'><?!@#^&%=+`$[]{}," + '"')
        textCtrl.SetValue(text)

        if len(text) < 3:
            self.dlg = ValidatorMsgDialog(None, "Логин состоит минимум из 3 символов!")
            self.dlg.ShowModal()
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True