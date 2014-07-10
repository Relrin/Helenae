# -*- coding: utf-8
import os
import wx

ID_NOTEBOOK_CTRL = 2000
ID_BUTTON_SAVE = 2001
ID_BUTTON_CANCEL_SAVE = 2002
ID_TAB_ONE = 2003
ID_TAB_ONE_CRYPTO_CHECKBOX = 2004
ID_TAB_ONE_INPUT_USER_FOLDER = 2005
ID_TAB_ONE_INPUT_USER_BUTTON = 2006


class TabPanelBasics(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=ID_TAB_ONE)

        self.LabelCrypto = wx.StaticText(self, label='Алгоритм шифрования:', pos=(15, 15))

        self.crypto = ['AES-256',]
        self.ComboBox = wx.ComboBox(self, choices=self.crypto, style=wx.CB_READONLY, pos=(160, 10), value=self.crypto[0])

        self.LabelUserFolder = wx.StaticText(self, label='Текущий каталог:', pos=(15, 45))
        self.InputUserFolder = wx.TextCtrl(self, ID_TAB_ONE_INPUT_USER_FOLDER, size=(214, -1), pos=(130, 40), style=wx.TE_READONLY)
        self.InputUserFolder.SetBackgroundColour('#D9D9D9')
        self.InputButton = wx.Button(self, id=ID_TAB_ONE_INPUT_USER_BUTTON, label='..', size=(25, 23), pos=(350, 40))

        self.FolderDialog = wx.DirDialog(self, "Выберите каталог для хранения файлов", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        self.Bind(wx.EVT_BUTTON, self.ShowDirDialog, id=ID_TAB_ONE_INPUT_USER_BUTTON)

    def ShowDirDialog(self, event):
        if self.FolderDialog.ShowModal() == wx.ID_OK:
           self.InputUserFolder.SetValue(self.FolderDialog.GetPath())


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
        self.parent = parent

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
        self.Bind(wx.EVT_CLOSE, self.CloseOptionsWindow)

        # absolute positioning
        self.panel.SetSizer(self.sizer)
        self.Layout()

        # icon for app
        self.icon = wx.Icon(ico_folder+'/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.__setUserFolder()
        self.createUsersFolder()

    def __setUserFolder(self):
        sp = wx.StandardPaths.Get()
        self.userFolder = sp.GetDocumentsDir() + '/CloudStorage/users/'

    def setUserOptionsPath(self, user):
        self.userOptionsPath = self.userFolder + user + '.opt'

    def setUserFolderOnFirstLoad(self):
        while self.notebook.tabBasicPreferences.FolderDialog.ShowModal() != wx.ID_OK:
            pass
        pathToUserFolder = self.notebook.tabBasicPreferences.FolderDialog.GetPath()
        self.notebook.tabBasicPreferences.InputUserFolder.SetValue(pathToUserFolder)
        self.parent.files_folder.showFilesInDirectory(pathToUserFolder)

    def createUsersFolder(self):
        if not os.path.exists(self.userFolder):
            os.makedirs(self.userFolder)

    def createOptionsFile(self):
        if not os.path.exists(self.userOptionsPath):
            self.writeUserSetting()

    def userOptionsFileExists(self, user):
        pathToUserOptionsFile = self.userFolder + user + '.opt'
        return os.path.exists(pathToUserOptionsFile)

    def readUserSettings(self):
        import shelve
        shelve = shelve.open(self.userOptionsPath)
        self.notebook.tabBasicPreferences.ComboBox.SetValue(shelve['crypto-alg'])
        self.notebook.tabBasicPreferences.InputUserFolder.SetValue(shelve['user-folder'])
        shelve.close()

    def writeUserSetting(self):
        import shelve
        shelve = shelve.open(self.userOptionsPath, writeback=True)
        userFolder = self.notebook.tabBasicPreferences.InputUserFolder.GetValue()
        self.parent.sb.SetStatusText(userFolder)
        self.parent.files_folder.setCurrentDir(userFolder)
        self.parent.files_folder.showFilesInDirectory(userFolder)
        shelve['crypto-alg'] = self.notebook.tabBasicPreferences.ComboBox.GetValue()
        shelve['user-folder'] = userFolder
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
    frame = OptionsCtrl(None, -1, 'Опции', ico_folder)
    frame.Show()
    app.MainLoop()