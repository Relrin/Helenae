# -*- coding: utf-8 -*-
import wx


class PasswordValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):  # Required method for validator
        return PasswordValidator()

    def TransferToWindow(self):
        return True   # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True   # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue().encode('utf-8')

        if len(text) < 6:
            wx.MessageBox("Пароль состоит минимум из 6 символов!", "Ошибка")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True