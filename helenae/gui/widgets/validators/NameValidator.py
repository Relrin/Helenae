# -*- coding: utf-8 -*-
import wx
from ValidatorMsgDlg import ValidatorMsgDialog


class NameValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.dlg = ValidatorMsgDialog

    def Clone(self):  # Required method for validator
        return NameValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8').strip()
        with_spaces = filter(lambda x: x!= '', text.split(' '))
        textCtrl.SetValue(' '.join(with_spaces))

        if len(text) < 5:
            self.dlg = ValidatorMsgDialog(None, "Ф.И.О. состоит минимум из 5 символов!")
            self.dlg.ShowModal()
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True