import wx
import wx.lib.agw.hyperlink as hl


class Faker():
    """
        This class is realized bot logic for UI testing
    """

    @staticmethod
    def clickButton(frame, idButton):
        fakeClickButton = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, idButton)
        assert frame.ProcessEvent(fakeClickButton) is True

    @staticmethod
    def clickHyperlink(frame, idHyperlink):
        fakeClickHyperlink = wx.CommandEvent(hl.wxEVT_HYPERLINK_LEFT, idHyperlink)
        assert frame.ProcessEvent(fakeClickHyperlink) is True

    @staticmethod
    def clickMenuItem(frame, idMenuItem):
        fakeClickMenuItem = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, idMenuItem)
        assert frame.ProcessEvent(fakeClickMenuItem) is True

    @staticmethod
    def clickButtonDialogOK(frame):
        clickEvent = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK)
        frame.dlg.ProcessEvent(clickEvent)


    @staticmethod
    def enterFakeLogin(frame, login, psw):
        frame.login_input.SetValue(login)
        frame.pass_input.SetValue(psw)

    @staticmethod
    def enterFakeRegisterData(frame, login, psw, fullname, email):
        frame.login_input.SetValue(login)
        frame.pass_input.SetValue(psw)
        frame.fullname_input.SetValue(fullname)
        frame.email_input.SetValue(email)