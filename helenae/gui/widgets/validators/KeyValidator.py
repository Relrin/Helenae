# -*- coding: utf-8 -*-
import wx
from ValidatorMsgDlg import ValidatorMsgDialog


class KeyValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.dlg = None

    def Clone(self):  # Required method for validator
        return KeyValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8').strip().replace(' ', '')
        text = text.translate(None, "~|*:'><?!@#^&%=+`$[]{}," + '"')
        textCtrl.SetValue(text)

        if len(text) != 32:
            self.dlg = ValidatorMsgDialog(None, "Ключ шифрования должен состоять из 32 символов!")
            self.dlg.ShowModal()
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour('#D9D9D9')
            textCtrl.Refresh()
            return True