# -*- coding: utf-8
import os
import wx

ID_NOTEBOOK_CTRL = 2000
ID_BUTTON_SAVE = 2001
ID_BUTTON_CANCEL_SAVE = 2002
ID_TAB_ONE = 2003
ID_TAB_ONE_CRYPTO_CHECKBOX = 2004


class TabPanelBasics(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=ID_TAB_ONE)

        self.LabelCrypto = wx.StaticText(self, label='Алгоритм шифрования:', pos=(15, 15))

        self.crypto = ['AES-256',]
        self.ComboBox = wx.ComboBox(self, choices=self.crypto, style=wx.CB_READONLY, pos=(160, 10), value=self.crypto[0])


class NotebookCtrl(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=ID_NOTEBOOK_CTRL, style=wx.BK_DEFAULT)

        self.tabBasicPreferences = TabPanelBasics(self)
        self.AddPage(self.tabBasicPreferences, "Общие")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()


class OptionsCtrl(wx.Frame):
    """
        Frame that holds all other widgets
    """
    def __init__(self, parent, id, title, ico_folder):
        wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # user preferences
        self.userFolder = './user/'
        self.userOptionsPath = ''
        self.panel = wx.Panel(self)

        # option tabs
        self.notebook = NotebookCtrl(self.panel)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)

        # button panel
        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.accept_button = wx.Button(self.panel, id=ID_BUTTON_SAVE, label='Сохранить')
        self.cancel_button = wx.Button(self.panel, id=ID_BUTTON_CANCEL_SAVE, label='Отмена')
        self.sizer_h.Add(self.accept_button, 0, wx.LEFT, border=214)
        self.sizer_h.Add(self.cancel_button, 0, wx.LEFT, border=5)
        self.sizer.AddSizer(self.sizer_h)

        # events
        self.Bind(wx.EVT_BUTTON, self.CloseOptionsWindowAndSave, id=ID_BUTTON_SAVE)
        self.Bind(wx.EVT_BUTTON, self.CloseOptionsWindow, id=ID_BUTTON_CANCEL_SAVE)

        # absolute positioning
        self.panel.SetSizer(self.sizer)
        self.Layout()

        # icon for app
        self.icon = wx.Icon(ico_folder+'/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.createUsersFolder()

    def setUserOptionsPath(self, user):
        self.userOptionsPath = self.userFolder + user + '.txt'
        self.createOptionsFile()

    def createUsersFolder(self):
        if not os.path.exists(self.userFolder):
            os.mkdir(self.userFolder)

    def createOptionsFile(self):
        if not os.path.exists(self.userOptionsPath):
            self.writeUserSetting()
        else:
            self.readUserSettings()

    def readUserSettings(self):
        import shelve
        shelve = shelve.open(self.userOptionsPath)
        self.notebook.tabBasicPreferences.ComboBox.SetValue(shelve['crypto-alg'])
        shelve.close()

    def writeUserSetting(self):
        import shelve
        shelve = shelve.open(self.userOptionsPath, writeback=True)
        shelve['crypto-alg'] = self.notebook.tabBasicPreferences.ComboBox.GetValue()
        shelve.close()

    def CloseOptionsWindowAndSave(self, event):
        self.writeUserSetting()
        self.Hide()

    def CloseOptionsWindow(self, event):
        self.readUserSettings()
        self.Hide()


if __name__ == "__main__":
    app = wx.App(0)
    ico_folder = '..'
    frame = OptionsCtrl(None, -1, 'Опции', ico_folder, 'relrin')
    frame.Show()
    app.MainLoop()