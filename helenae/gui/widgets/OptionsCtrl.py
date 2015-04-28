# -*- coding: utf-8
import os
import wx
import random
import string

from InputDialogCtrl import InputDialog
from validators.KeyValidator import KeyValidator

import platform

ID_NOTEBOOK_CTRL = 2000
ID_BUTTON_SAVE = 2001
ID_BUTTON_CANCEL_SAVE = 2002
ID_TAB_ONE = 2003
ID_TAB_ONE_CRYPTO_CHECKBOX = 2004
ID_TAB_ONE_INPUT_USER_FOLDER = 2005
ID_TAB_ONE_INPUT_USER_BUTTON = 2006
ID_TAB_ONE_INPUT_CRYPT_PSW = 2007
ID_TAB_ONE_INPUT_CRYPT_BUTTON = 2008


class TabPanelBasics(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=ID_TAB_ONE)

        # Mac OS X
        if platform.system() == 'Darwin':
            ComboBoxPos = (175, 10)
            InputTextCtrlPos = (145, 45)
            InputButtonPos = (365, 40)
            ErrorLabelFontSize = 10
            ErrorLabelPos =(15, 105)
        # Windows/Linux
        else:
            ComboBoxPos = (160, 10)
            InputTextCtrlPos = (130, 40)
            InputButtonPos = (350, 40)
            ErrorLabelFontSize = 7
            ErrorLabelPos =(15, 155)

        self.parent = parent

        self.LabelCrypto = wx.StaticText(self, label='Алгоритм шифрования:', pos=(15, 15))

        self.crypto = ['AES-256', 'Twofish', 'Serpent']
        self.ComboBox = wx.ComboBox(self, choices=self.crypto, style=wx.CB_READONLY, pos=ComboBoxPos, value=self.crypto[0])

        self.LabelUserFolder = wx.StaticText(self, label='Текущий каталог:', pos=(15, 45))
        self.InputUserFolder = wx.TextCtrl(self, ID_TAB_ONE_INPUT_USER_FOLDER, size=(214, -1), pos=InputTextCtrlPos, style=wx.TE_READONLY)
        self.InputUserFolder.SetBackgroundColour('#D9D9D9')
        self.InputButton = wx.Button(self, id=ID_TAB_ONE_INPUT_USER_BUTTON, label='..', size=(25, 23), pos=InputButtonPos)

        self.LabelCryptPassword= wx.StaticText(self, label='Ключ шифрования:', pos=(15, 75))
        self.InputCryptPassword = wx.TextCtrl(self, ID_TAB_ONE_INPUT_CRYPT_PSW, size=(214, -1), pos=(InputTextCtrlPos[0], InputTextCtrlPos[1]+30), style=wx.TE_READONLY)
        self.InputCryptPassword.SetBackgroundColour('#D9D9D9')
        self.InputButton = wx.Button(self, id=ID_TAB_ONE_INPUT_CRYPT_BUTTON, label='..', size=(25, 23), pos=(InputButtonPos[0], InputButtonPos[1]+30))

        self.error_login = wx.StaticText(self, label='В случае удаления файла с настройками, ключ шифрования будет\nтакже утерян! Пожалуйста, сохраните где-нибудь ключ шифрования!', pos=ErrorLabelPos)
        self.error_login.SetForegroundColour('#DE4421')
        self.error_login.SetFont((wx.Font(ErrorLabelFontSize, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0)))

        self.FolderDialog = wx.DirDialog(self, "Выберите каталог для хранения файлов", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        self.Bind(wx.EVT_BUTTON, self.ShowDirDialog, id=ID_TAB_ONE_INPUT_USER_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.InputCryptoKey, id=ID_TAB_ONE_INPUT_CRYPT_BUTTON)

    def ShowDirDialog(self, event):
        if self.FolderDialog.ShowModal() == wx.ID_OK:
           self.InputUserFolder.SetValue(self.FolderDialog.GetPath())

    def InputCryptoKey(self, event):
        dlg = InputDialog(self, -1, 'Введите ключ шифования', self.parent.parent.ico_folder, KeyValidator(), lable_name='Значение ключа')
        dlg.ShowModal()
        if dlg.result is not None:
            self.InputCryptPassword.SetValue(dlg.result)
        dlg.Destroy()


class NotebookCtrl(wx.Notebook):
    def __init__(self, parent, frame):
        wx.Notebook.__init__(self, parent, id=ID_NOTEBOOK_CTRL, style=wx.BK_DEFAULT)
        self.parent = frame

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

        if platform.system():
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE &
                                                             ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
            DefaultBorderSave = 249
            DefaultBorderCancel = 10
            ButtonCancelFlags = wx.LEFT ^ wx.BOTTOM
            size = (440, 265)
            self.SetSize(size)
        else:
            wx.Frame.__init__(self, parent, -1, title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            DefaultBorderSave = 214
            DefaultBorderCancel = 5
            ButtonCancelFlags = wx.LEFT

        self.parent = parent
        self.ico_folder = ico_folder

        # user preferences
        self.userFolder = './user/'
        self.userOptionsPath = ''
        self.panel = wx.Panel(self)

        # option tabs
        self.notebook = NotebookCtrl(self.panel, self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)

        # button panel
        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.accept_button = wx.Button(self.panel, id=ID_BUTTON_SAVE, label='Сохранить')
        self.cancel_button = wx.Button(self.panel, id=ID_BUTTON_CANCEL_SAVE, label='Отмена')
        self.sizer_h.Add(self.accept_button, 0, wx.LEFT, border=DefaultBorderSave)
        self.sizer_h.Add(self.cancel_button, 0, ButtonCancelFlags, border=DefaultBorderCancel)
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
        self.Center()

    def generateKey(self):
        key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in xrange(32))
        self.notebook.tabBasicPreferences.InputCryptPassword.SetValue(key)

    def getCryptoKey(self):
        return self.notebook.tabBasicPreferences.InputCryptPassword.GetValue()

    def __setUserFolder(self):
        sp = wx.StandardPaths.Get()
        self.userFolder = sp.GetDocumentsDir() + '/CloudStorage/users/'
        self.tmpFolder = sp.GetDocumentsDir() + '/CloudStorage/users/tmp/'

    def setUserOptionsPath(self, user):
        self.userOptionsPath = self.userFolder + user + '.opt'

    def setUserFolderOnFirstLoad(self):
        while self.notebook.tabBasicPreferences.FolderDialog.ShowModal() != wx.ID_OK:
            pass
        pathToUserFolder = self.notebook.tabBasicPreferences.FolderDialog.GetPath()
        self.notebook.tabBasicPreferences.InputUserFolder.SetValue(pathToUserFolder)
        self.parent.files_folder.showFilesInDirectory(pathToUserFolder)
        self.generateKey()

    def getCryptoAlgorithm(self):
        return self.notebook.tabBasicPreferences.ComboBox.GetValue()

    def createUsersFolder(self):
        if not os.path.exists(self.userFolder):
            try:
                os.makedirs(self.userFolder)
            except OSError:
                pass
        if not os.path.exists(self.tmpFolder):
            try:
                os.makedirs(self.tmpFolder)
            except OSError:
                pass

    def checkUserFolder(self):
        userFolder = self.notebook.tabBasicPreferences.InputUserFolder.GetValue() + '/'
        if not os.path.exists(userFolder):
            try:
                os.makedirs(userFolder)
            except OSError:
                pass

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
        self.notebook.tabBasicPreferences.InputCryptPassword.SetValue(shelve['crypto-key'])
        self.checkUserFolder()
        shelve.close()

    def writeUserSetting(self):
        import shelve
        shelve = shelve.open(self.userOptionsPath, writeback=True)
        userFolder = self.notebook.tabBasicPreferences.InputUserFolder.GetValue() + '/'
        self.parent.sb.SetStatusText(userFolder)
        self.parent.files_folder.setCurrentDir(userFolder)
        self.parent.files_folder.setUsersDir(userFolder)
        self.parent.files_folder.showFilesInDirectory(userFolder)
        shelve['crypto-alg'] = self.notebook.tabBasicPreferences.ComboBox.GetValue()
        shelve['crypto-key'] = self.notebook.tabBasicPreferences.InputCryptPassword.GetValue()
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