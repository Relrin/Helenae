# -*- coding: utf-8 -*-
import os
import wx
import shutil
import ntpath

from FileListCtrl import FileListCtrl
from OptionsCtrl import OptionsCtrl
from AboutCtrl import About
from InputDialogCtrl import InputDialog
from validators.FolderValidator import FolderValidator
from validators.FileValidator import FileValidator
from validators.ValidatorMsgDlg import ValidatorMsgDialog as MsgDlg

ID_BUTTON = 100
ID_BUTTON_WRITE = 101
ID_BUTTON_TRANSFER = 102
ID_BUTTON_CREATE_FOLDER = 103
ID_BUTTON_REMOVE_FILE = 104
ID_BUTTON_RENAME = 105
ID_NEW = 150
ID_FOLDER = 151
ID_RENAME = 152
ID_REPLACE = 153
ID_REMOVE = 154
ID_SHOW_STATUSBAR = 155
ID_OPTIONS = 156
ID_WRITE = 157
ID_COPY_FILE = 158
ID_COPY_FOLDER = 159
ID_CREATE_LINK = 160
ID_COPY_FILE_LINK = 161
ID_EXIT = 200
ID_SPLITTER = 300
ID_TOOLBAR_UPDIR = 201
ID_TOOLBAR_HOME = 202
ID_TOOLBAR_REFRESH = 203
ID_TOOLBAR_HELP = 204
ID_TOOLBAR_ABOUT = 205

# TODO: save part info (about catalog structure) in XML


class FileManager(wx.Frame):
    def __init__(self, parent, id, title, ico_folder):
        wx.Frame.__init__(self, parent, -1, title)
        self.parent = parent
        self.ico_folder = ico_folder
        wx.Log.SetLogLevel(0)

        # file frame
        self.files_folder = FileListCtrl(self, -1, ico_folder)
        # options frame
        self.options_frame = OptionsCtrl(self, -1, "Options", ico_folder)
        # about frame
        self.about_frame = About(self, -1, 'About', ico_folder)

        # menu
        filemenu= wx.Menu()
        newItem = wx.MenuItem(filemenu, ID_NEW, "&New file\tShift+1", help='Create new file in directory')
        newItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/new.png'))
        createItem = wx.MenuItem(filemenu, ID_FOLDER, "&Create directory\tShift+2", help='Create new directory')
        createItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/folder.png'))

        createLinkItem = wx.MenuItem(filemenu, ID_CREATE_LINK, "&Create shared link\tF1", help='Create link for chosen file')
        createLinkItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/link.png'))
        copyFileByLinkItem = wx.MenuItem(filemenu, ID_COPY_FILE_LINK, "&Download file by shared link\tF2", help='Download file by shared link')
        copyFileByLinkItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/download_cloud.png'))

        copyFileItem = wx.MenuItem(filemenu, ID_COPY_FILE, "&Copy file\tF3", help='Copy file from outside to current directory')
        copyFileItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/copy_file.png'))
        copyFolderItem = wx.MenuItem(filemenu, ID_COPY_FOLDER, "&Copy directory\tF4", help='Copy directory from outside to current directory')
        copyFolderItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/copy_folder.png'))

        writeItem = wx.MenuItem(filemenu, ID_WRITE, "&Write\tCtrl+W", help='Write chosen files')
        writeItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/write.png'))
        transferItem = wx.MenuItem(filemenu, ID_REPLACE, "&Replace\tCtrl+T", help='Replace chosen files to another directory')
        transferItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/remove.png'))
        deleteItem = wx.MenuItem(filemenu, ID_REMOVE, "&Delete\tCtrl+D", help='Delete chosen files')
        deleteItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/delete.png'))
        renameItem = wx.MenuItem(filemenu, ID_RENAME, "&Rename\tCtrl+R", help='Rename chosen file or directory')
        renameItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/rename.png'))
        filemenu.AppendItem(newItem)
        filemenu.AppendItem(createItem)
        filemenu.AppendSeparator()
        filemenu.AppendItem(createLinkItem)
        filemenu.AppendItem(copyFileByLinkItem)
        filemenu.AppendSeparator()
        filemenu.AppendItem(copyFileItem)
        filemenu.AppendItem(copyFolderItem)
        filemenu.AppendSeparator()
        filemenu.AppendItem(renameItem)
        filemenu.AppendItem(transferItem)
        filemenu.AppendItem(writeItem)
        filemenu.AppendItem(deleteItem)
        filemenu.AppendSeparator()
        exitItem = wx.MenuItem(filemenu, ID_EXIT, "&Exit", help='Exit for application')
        exitItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/file/exit.png'))
        filemenu.AppendItem(exitItem)

        configmenu = wx.Menu()
        self.show_statusbar = configmenu.Append(ID_SHOW_STATUSBAR, 'Show status bar', 'Show status bar', kind=wx.ITEM_CHECK)
        configmenu.Check(self.show_statusbar.GetId(), True)
        self.preferencesItem = wx.MenuItem(filemenu, ID_OPTIONS, "&Options\tCtrl+O", help='Base options for application')
        self.preferencesItem.SetBitmap(wx.Bitmap(ico_folder + '/icons/ui/menu/preferences/preferences.png'))
        configmenu.AppendItem(self.preferencesItem)

        self.menuBar = wx.MenuBar()
        self.menuBar.Append(filemenu, "&File")
        self.menuBar.Append(configmenu, "&Preferences")

        # toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        tb.AddSimpleTool(ID_TOOLBAR_UPDIR, wx.Bitmap(ico_folder + '/icons/ui/toolbar/up.png'), 'Go to uppper directory')
        tb.AddSimpleTool(ID_TOOLBAR_HOME, wx.Bitmap(ico_folder + '/icons/ui/toolbar/home.png'), 'Home')
        tb.AddSimpleTool(ID_TOOLBAR_REFRESH, wx.Bitmap(ico_folder + '/icons/ui/toolbar/refresh.png'), 'Refresh current directory')
        tb.AddSeparator()
        tb.AddSimpleTool(ID_TOOLBAR_HELP, wx.Bitmap(ico_folder + '/icons/ui/toolbar/help.png'), 'Help')
        tb.AddSimpleTool(ID_TOOLBAR_ABOUT, wx.Bitmap(ico_folder + '/icons/ui/toolbar/about.png'), 'Authors')
        tb.Realize()

        # button panel
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        button1 = wx.Button(self, ID_BUTTON_WRITE, "Write")
        button1.SetBackgroundColour('#BFD8DF')
        button1.SetForegroundColour("#2F4D57")

        button2 = wx.Button(self, ID_BUTTON_TRANSFER, "Replace")
        button2.SetBackgroundColour('#BFD8DF')
        button2.SetForegroundColour("#2F4D57")

        button3 = wx.Button(self, ID_BUTTON_CREATE_FOLDER, "Create directory")
        button3.SetBackgroundColour('#BFD8DF')
        button3.SetForegroundColour("#2F4D57")

        button4 = wx.Button(self, ID_BUTTON_REMOVE_FILE, "Delete")
        button4.SetBackgroundColour('#BFD8DF')
        button4.SetForegroundColour("#2F4D57")

        button5 = wx.Button(self, ID_BUTTON_RENAME, "Rename")
        button5.SetBackgroundColour('#BFD8DF')
        button5.SetForegroundColour("#2F4D57")

        button6 = wx.Button(self, ID_EXIT, "Exit")
        button6.SetBackgroundColour('#BFD8DF')
        button6.SetForegroundColour("#2F4D57")

        self.sizer2.Add(button1, 1, wx.EXPAND)
        self.sizer2.Add(button2, 1, wx.EXPAND)
        self.sizer2.Add(button3, 1, wx.EXPAND)
        self.sizer2.Add(button4, 1, wx.EXPAND)
        self.sizer2.Add(button5, 1, wx.EXPAND)
        self.sizer2.Add(button6, 1, wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.files_folder, 1,wx.EXPAND)
        self.sizer.Add(self.sizer2, 0,wx.EXPAND)
        self.SetSizer(self.sizer)

        # events bindings
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, self.show_statusbar)
        self.Bind(wx.EVT_MENU, self.ShowMenu, self.preferencesItem)
        self.Bind(wx.EVT_CLOSE, self.OnExitProgramm)
        # create folder
        self.Bind(wx.EVT_BUTTON, self.OnCreateFolder, id=ID_BUTTON_CREATE_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnCreateFolder, id=ID_FOLDER)
        # create file
        self.Bind(wx.EVT_MENU, self.OnCreateFile, id=ID_NEW)
        # toolbar events
        self.Bind(wx.EVT_TOOL, self.UpDir, id=ID_TOOLBAR_UPDIR)
        self.Bind(wx.EVT_TOOL, self.Home, id=ID_TOOLBAR_HOME)
        self.Bind(wx.EVT_TOOL, self.RefreshFileCtrl, id=ID_TOOLBAR_REFRESH)
        self.Bind(wx.EVT_TOOL, self.ShowAbout, id=ID_TOOLBAR_ABOUT)
        # copy file
        self.Bind(wx.EVT_MENU, self.CopyFile, id=ID_COPY_FILE)
        # copy folder
        self.Bind(wx.EVT_MENU, self.CopyFolder, id=ID_COPY_FOLDER)

        # set hotkeys for program
        self.accel_tbl = wx.AcceleratorTable([
                                               # File menu hotkeys
                                                (wx.ACCEL_SHIFT, ord('1'), ID_NEW)
                                               ,(wx.ACCEL_SHIFT, ord('2'), ID_FOLDER)
                                               ,(wx.WXK_F1, None, ID_CREATE_LINK)
                                               ,(wx.WXK_F2, None, ID_COPY_FILE_LINK)
                                               ,(wx.WXK_F3, None, ID_COPY_FILE)
                                               ,(wx.WXK_F4, None, ID_COPY_FOLDER)
                                               ,(wx.ACCEL_CTRL, ord('W'), ID_WRITE)
                                               ,(wx.ACCEL_CTRL, ord('T'), ID_REPLACE)
                                               ,(wx.ACCEL_CTRL, ord('D'), ID_REMOVE)
                                               ,(wx.ACCEL_CTRL, ord('R'), ID_RENAME)
                                               # Options hotkeys
                                               ,(wx.ACCEL_CTRL, ord('O'), ID_OPTIONS)
                                             ])
        self.SetAcceleratorTable(self.accel_tbl)


        # define size and icon for app
        size = (800, 600)
        self.SetSize(size)
        self.icon = wx.Icon(ico_folder + '/icons/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize(size)
        self.Center()

    def UpDir(self, event):
        if self.files_folder.currentDir != self.files_folder.defaultDir:
            self.files_folder.currentDir = self.files_folder.getParentDir(self.files_folder.currentDir)
        filepath = self.files_folder.currentDir
        self.files_folder.showFilesInDirectory(filepath)

    def Home(self, event):
        self.files_folder.currentDir = self.files_folder.defaultDir
        self.files_folder.showFilesInDirectory(self.files_folder.defaultDir)

    def RefreshFileCtrl(self, event):
        self.files_folder.showFilesInDirectory(self.files_folder.currentDir)

    def OnCreateFolder(self, event):
        dlg = InputDialog(self, -1, "Enter directory name", self.ico_folder, FolderValidator())
        if dlg.ShowModal() == wx.ID_OK:
            try:
                new_folder = self.files_folder.currentDir + dlg.result
                os.makedirs(new_folder)
            except OSError:
                wx.MessageBox("This directory already exists!\nPlease, type another name.", 'Error')
            except Exception, exc:
                wx.MessageBox("%s" % exc.message, "Error")
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)
        dlg.Destroy()

    def OnCreateFile(self, event):
        dlg = InputDialog(self, -1, "Type file name and extension", self.ico_folder, FileValidator())
        if dlg.ShowModal() == wx.ID_OK:
            try:
                new_file = self.files_folder.currentDir + dlg.result
                new_folders, filename = ntpath.split(dlg.result)
                if len(new_folders) > 0 and len(new_folders.split('/')) >= 1:
                    try:
                        os.makedirs(self.files_folder.currentDir + new_folders)
                    except OSError:
                        pass
                    except Exception, exc:
                        wx.MessageBox("%s" % exc.message, "Error")
                if os.path.exists(new_file):
                    raise OSError()
                open(new_file, 'a').close()
            except OSError:
                wx.MessageBox("This file already exists!\nPlease, type another name.", 'Error')
            except Exception, exc:
                wx.MessageBox("%s" % exc.message, "Error")
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)
        dlg.Destroy()

    def CopyFile(self, event):
        dlg = wx.FileDialog(self, "Choose path to file", "", "", "All files (*.*)|*.*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            dir, filename = ntpath.split(filepath)
            shutil.copyfile(filepath, self.files_folder.currentDir+filename)
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)
            msg_dlg = MsgDlg(None, "Copying completed!")
            msg_dlg.ShowModal()
        dlg.Destroy()

    def CopyMoveOperation(self, src, target, operation='copy'):
        for src_dir, dirs, files in os.walk(src):
            dst_dir = src_dir.replace(src, target)
            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                if operation is 'copy':
                    shutil.copy(src_file, dst_dir)
                elif operation is 'move':
                    shutil.move(src_file, dst_dir)

    def CopyFolder(self, event):
        dlg = wx.DirDialog(self, "Choose directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            folderpath = dlg.GetPath()
            try:
                new_folder = folderpath.split('/')[-1]
                os.mkdir(new_folder)
            # if this folder already exists - then catch exception, ignore him, and copy files right now
            except OSError:
                pass
            self.CopyMoveOperation(folderpath, self.files_folder.currentDir+new_folder)
            self.files_folder.showFilesInDirectory(self.files_folder.currentDir)
            msg_dlg = MsgDlg(None, "Copying completed!")
            msg_dlg.ShowModal()
        dlg.Destroy()

    def ShowMenu(self, event):
        self.options_frame.Show()

    def ShowAbout(self, event):
        self.about_frame.Show()

    def ToggleStatusBar(self, event):
        if self.show_statusbar.IsChecked():
            self.sb.Show()
        else:
            self.sb.Hide()

    def OnExit(self, event):
        self.Close()

    def OnExitProgramm(self, event):
        self.parent.Close()

    def OnSize(self, event):
        size = self.GetSize()
        self.files_folder.ResizeColumns(size.x)
        cwd = os.getcwd()
        try:
            self.sb.SetStatusText(cwd)
        except AttributeError:
            self.sb = self.CreateStatusBar()
            self.sb.SetStatusText(cwd)
        except wx.PyDeadObjectError:
            pass
        event.Skip()

if __name__ == '__main__':
    app = wx.App(0)
    ico_folder = '..'
    frame = FileManager(None, -1, 'Helenae', ico_folder)
    frame.Show(True)
    app.MainLoop()
