# -*- coding: utf-8 -*-
"""
    Implementation of GUI client for Helenae project.
    At this file, as you can see, written wrapper for GUI, which founded in /gui/ folder.
    For UI using only wxPython. Also "patched" twisted event-loop for support event-loop from wxPython
"""
import os
import shutil
from json import loads, dumps
from random import randint
from subprocess import Popen, PIPE, STDOUT
from optparse import OptionParser

import wx
from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor, ssl, threads

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from utils.jsonConstructor import constructDataClient, dumpConfigToJSON
from utils.crypto.md5 import md5_for_file
from utils.wx.CustomEvents import UpdateFileListCtrlEvent, EVT_UPDATE_FILE_LIST_CTRL
from utils.filesystem import getFileList

from gui.CloudStorage import CloudStorage, ID_BUTTON_ACCEPT
from gui.widgets.Filemanager import ID_BUTTON_WRITE, ID_WRITE, ID_BUTTON_REMOVE_FILE, ID_REMOVE, \
    ID_BUTTON_RENAME, ID_RENAME, ID_BUTTON_TRANSFER, ID_REPLACE, ID_CREATE_LINK, ID_COPY_FILE_LINK
from gui.widgets.RegisterCtrl import ID_BUTTON_REG
from gui.widgets.CompleteRegCtrl import ID_BUTTON_CLOSE_MSG
from gui.widgets.InputDialogCtrl import InputDialog
from gui.widgets.InputLinkCtrl import InputLink
from gui.widgets.validators.RenameValidator import RenameValidator


class GUIClientProtocol(WebSocketClientProtocol):

    gui = None

    def __init__(self):
        self.login = None
        self.commands = self.__initHandlers()

    def __initHandlers(self):
        handlers = {}
        # basic commands
        handlers['AUTH'] = self.__AUTH
        handlers['CREG'] = self.__CREG
        handlers['READ'] = self.__READ
        handlers['WRTE'] = self.__WRTE
        handlers['DELT'] = self.__DELT
        handlers['RENF'] = self.__RENF
        handlers['REPF'] = self.__REPF
        handlers['CRLN'] = self.__CRLN
        handlers['LINK'] = self.__LINK
        # continues operations...
        handlers['RAUT'] = self.__RAUT
        handlers['RREG'] = self.__RREG
        handlers['CREA'] = self.__CREA
        handlers['CWRT'] = self.__CWRT
        handlers['CDLT'] = self.__CDLT
        handlers['CREN'] = self.__CREN
        handlers['CCLN'] = self.__CCLN
        handlers['CLNK'] = self.__CLNK
        return handlers

    def initBindings(self):
        self.gui.Bind(wx.EVT_BUTTON, self.__StartAuth, id=ID_BUTTON_ACCEPT)
        self.gui.RegisterWindow.Bind(wx.EVT_BUTTON, self.__StartRegistration, id=ID_BUTTON_REG)
        self.gui.Bind(wx.EVT_BUTTON, self.onEndRegister, id=ID_BUTTON_CLOSE_MSG)
        self.gui.Bind(EVT_UPDATE_FILE_LIST_CTRL, self.onUpdateListCtrl)
        # write files/folder
        self.gui.Bind(wx.EVT_BUTTON, self.__WRTE, id=ID_BUTTON_WRITE)
        self.gui.Bind(wx.EVT_MENU, self.__WRTE, id=ID_WRITE)
        # delete file/folder
        self.gui.Bind(wx.EVT_BUTTON, self.__DELT, id=ID_BUTTON_REMOVE_FILE)
        self.gui.Bind(wx.EVT_MENU, self.__DELT, id=ID_REMOVE)
        # rename file/folder
        self.gui.Bind(wx.EVT_BUTTON, self.__RENF, id=ID_BUTTON_RENAME)
        self.gui.Bind(wx.EVT_MENU, self.__RENF, id=ID_RENAME)
        # replace file/folder
        self.gui.Bind(wx.EVT_BUTTON, self.__REPF, id=ID_BUTTON_TRANSFER)
        self.gui.Bind(wx.EVT_MENU, self.__REPF, id=ID_REPLACE)
        # create link on file
        self.gui.Bind(wx.EVT_MENU, self.__CRLN, id=ID_CREATE_LINK)
        # download file by link
        self.gui.Bind(wx.EVT_MENU, self.__LINK, id=ID_COPY_FILE_LINK)

    def __SendInfoToFileServer(self, json_path, ip, port):
        p = Popen(["python", "./fileserver_client.py", str(json_path), str(ip), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        result = p.communicate()[0]

    def __StartAuth(self, event):
        """
            Event on 'Enter' button, which start auth procedure with server
        """
        self.gui.ClearErrorsLabels()
        if self.gui.login_input.GetValidator().Validate(self.gui.login_input) and \
                self.gui.pass_input.GetValidator().Validate(self.gui.pass_input):
            self.gui.PreloaderPlay()
            login = self.gui.login_input.GetValue().strip()
            password = self.gui.pass_input.GetValue().strip()
            data = constructDataClient('AUTH', login, password, False)
            self.sendMessage(data, sync=True)

    def __StartRegistration(self, event):
        self.gui.RegisterWindow.ClearErrorsLabels()
        if self.gui.RegisterWindow.login_input.GetValidator().Validate(self.gui.RegisterWindow.login_input) and \
                self.gui.RegisterWindow.pass_input.GetValidator().Validate(self.gui.RegisterWindow.pass_input) and \
                self.gui.RegisterWindow.fullname_input.GetValidator().Validate(self.gui.RegisterWindow.fullname_input):
            self.gui.RegisterWindow.PreloaderPlay()
            login = self.gui.RegisterWindow.login_input.GetValue().strip()
            password = self.gui.RegisterWindow.pass_input.GetValue().strip()
            fullname = self.gui.RegisterWindow.fullname_input.GetValue().strip()
            email = self.gui.RegisterWindow.email_input.GetValue().strip()
            data = dumps({'cmd': 'REGS', 'user': login, 'password': password, 'auth': False, 'error': [],
                          'email': email, 'fullname': fullname})
            self.sendMessage(data, sync=True)

    def onEndRegister(self, event):
        self.gui.RegisterWindow.Hide()
        self.gui.Close()
        self.gui.RegisterWindow.Close()

    def __AUTH(self, data):
        """
            Close login window and open filemanager window, only if successfull auth
        """
        if data['auth']:
            self.gui.Hide()
            self.gui.FileManager.options_frame.setUserOptionsPath(data['user'])
            if not self.gui.FileManager.options_frame.userOptionsFileExists(data['user']):
                self.gui.FileManager.options_frame.setUserFolderOnFirstLoad()
                self.gui.FileManager.options_frame.createOptionsFile()
            self.gui.FileManager.options_frame.readUserSettings()
            pathToUserFolder = self.gui.FileManager.options_frame.notebook.tabBasicPreferences.InputUserFolder.GetValue()
            self.gui.FileManager.files_folder.setCurrentDir(pathToUserFolder)
            self.gui.FileManager.files_folder.setUsersDir(pathToUserFolder)
            self.gui.FileManager.files_folder.showFilesInDirectory(self.gui.FileManager.files_folder.currentDir)
            self.gui.FileManager.sb.SetStatusText(pathToUserFolder)
            self.gui.FileManager.SetMenuBar(self.gui.FileManager.menuBar)
            self.gui.FileManager.Show()
            self.login = data['user']
            data = dumps({'cmd': 'GETF', 'user': data['user'], 'auth': True, 'error': []})
            self.sendMessage(data, sync=True)

    def __RAUT(self, data):
        """
            Handler for re-auth command, if incorrect user/password or something else...
        """
        for error_msg in data['error']:
            if 'User not found' in error_msg:
                self.gui.ShowErrorLogin('User not exists!')
            elif 'Incorrect password' in error_msg:
                self.gui.ShowErrorPassword('Invalid password!')

    def __CREG(self, data):
        """
            Handler for complete registration process
        """
        self.gui.RegisterWindow.PreloaderStop()
        self.gui.RegisterWindow.msg_box.Show()

    def __RREG(self, data):
        """
            Handler for re-registration process
        """
        self.gui.RegisterWindow.PreloaderStop()
        for error_msg in data['error']:
            if 'Length of username was been more than 3 symbols!' in error_msg:
                self.gui.RegisterWindow.ShowErrorLogin('Length of username was been more than 3 symbols!')
            if 'This user already exists' in error_msg:
                self.gui.RegisterWindow.ShowErrorLogin('This user already exists. Type another and...')
            if 'Length of password was been more than 6 symbols!' in error_msg:
                self.gui.RegisterWindow.ShowErrorPassword('Length of password was been more than 6 symbols!')
            if "Full name can't be empty!" in error_msg:
                self.gui.RegisterWindow.ShowErrorName("This can't be empty!")

    def __READ(self, data):
        base_dir = self.gui.FileManager.options_frame.notebook.tabBasicPreferences.InputUserFolder.GetValue() + '/'
        read_files = filter(lambda (folder, name): not os.path.exists(base_dir+folder+name), data['files_read'])
        del data['files_read']
        data = dumps({'cmd': 'REAF', 'user': self.login, 'auth': True, 'error': [], 'files_read': read_files})
        self.sendMessage(data, sync=True)

    def __CREA(self, data):
        """
            Massive reading files from file storage, using threads in Twisted
        """
        algorithm = self.gui.FileManager.options_frame.getCryptoAlgorithm()
        key = self.gui.FileManager.options_frame.getCryptoKey()
        tmp_dir = self.gui.FileManager.options_frame.tmpFolder
        user_folder = self.gui.FileManager.files_folder.getUsersDir()

        def defferedReadFile(user_id, name, path, file_id, servers):
            new_folders = os.path.normpath(user_folder + '/' + path)
            try:
                os.makedirs(new_folders)
            except OSError:
                pass
            for ip, port in servers:
                src_file = os.path.normpath(user_folder + '/' + path + '/' + name)
                server_ip = str(ip)
                server_port = str(port)
                json_file = os.path.normpath(tmp_dir + '/fsc_' + self.login + '_' + name + '_' + str(randint(0, 100000)) + '.json')
                dumpConfigToJSON(json_file, "READU_FILE", user_id, file_id, src_file, key, algorithm)
                self.__SendInfoToFileServer(json_file, server_ip, server_port)
                evt = UpdateFileListCtrlEvent()
                wx.PostEvent(self.gui, evt)

        for name, path, file_id, servers in data['files_read']:
            threads.deferToThread(defferedReadFile, data['user_id'], name, path, file_id, servers)
        del data['files_read']
        del data['user_id']

    def __WRTE(self, event):
        """
            Handler for massive write file from user directory to file servers
        """
        selectedItems = self.gui.FileManager.files_folder.getSelectedItems()
        if len(selectedItems) == 0:
            wx.MessageBox("For writing necessary choose file or directory!", "Message")
        else:
            write_files = []
            defaultDir = self.gui.FileManager.files_folder.defaultDir
            currentDir = self.gui.FileManager.files_folder.currentDir
            for item in selectedItems:
                path = os.path.normpath(currentDir + item)
                if os.path.isfile(path):
                    file_hash, size = md5_for_file(path)
                    write_files.append((item, currentDir, file_hash, size))
                elif os.path.isdir(path):
                    for root, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            folder = os.path.normpath(root) + '/'
                            file_path = os.path.normpath(os.path.join(root, filename))
                            file_hash, size = md5_for_file(file_path)
                            write_files.append((filename, folder, file_hash, size))
            data = dumps({'cmd': 'WRTF', 'user': self.login, 'auth': True, 'error': [], 'files_write': write_files,
                          'default_dir': defaultDir})
            self.sendMessage(data, sync=True)

    def __CWRT(self, data):
        """
            Multithreating write files to file servers
        """
        algorithm = self.gui.FileManager.options_frame.getCryptoAlgorithm()
        key = self.gui.FileManager.options_frame.getCryptoKey()
        tmp_dir = self.gui.FileManager.options_frame.tmpFolder

        def defferedWriteFile(user_id, cmd, name, path, file_id, servers):
            for server in servers:
                server_ip = str(server[0])
                server_port = str(server[1])
                src_file = os.path.normpath(path + '/' + name)
                json_file = os.path.normpath(tmp_dir + '/fsc_' + self.login + '_' + name + '_' + str(randint(0, 100000)) + '.json')
                dumpConfigToJSON(json_file, cmd, user_id, file_id, src_file, key, algorithm)
                self.__SendInfoToFileServer(json_file, server_ip, server_port)

        for cmd, name, path, file_id, servers in data['files_write']:
            threads.deferToThread(defferedWriteFile, data['user_id'], cmd, name, path, file_id, servers)
        del data['files_write']
        del data['user_id']

    def __DELT(self, event):
        """
            Create request for delete files
        """
        selectedItems = self.gui.FileManager.files_folder.getSelectedItems()
        if len(selectedItems) == 0:
            wx.MessageBox("For deleting necessary choose file or directory!", "Message")
        else:
            deleted_files = []
            defaultDir = self.gui.FileManager.files_folder.defaultDir
            currentDir = self.gui.FileManager.files_folder.currentDir
            for item in selectedItems:
                path = os.path.normpath(currentDir + item)
                if os.path.isfile(path):
                    file_hash, size = md5_for_file(path)
                    deleted_files.append((item, currentDir, file_hash, size))
                elif os.path.isdir(path):
                    if len(getFileList(path)) > 0:
                        for root, dirnames, filenames in os.walk(path):
                            for filename in filenames:
                                folder = os.path.normpath(root) + '/'
                                file_path = os.path.normpath(os.path.join(root, filename))
                                file_hash, size = md5_for_file(file_path)
                                deleted_files.append((filename, folder, file_hash, size))
                    else:
                        if os.path.exists(path):
                            shutil.rmtree(path)
                            evt = UpdateFileListCtrlEvent()
                            wx.PostEvent(self.gui, evt)
            data = dumps({'cmd': 'DELF', 'user': self.login, 'auth': True, 'error': [], 'deleted_files': deleted_files,
                          'default_dir': defaultDir})
            self.sendMessage(data, sync=True)

    def __CDLT(self, data):
        """
            Multithreating delete files
        """
        key = self.gui.FileManager.options_frame.getCryptoKey()
        tmp_dir = self.gui.FileManager.options_frame.tmpFolder

        def defferedDeleteFile(user_id, cmd, name, path, file_id, servers):
            for server in servers:
                server_ip = str(server[0])
                server_port = str(server[1])
                src_file = os.path.normpath(path + '/' + name)
                json_file = os.path.normpath(tmp_dir + '/fsc_' + self.login + '_' + name + '_' + str(randint(0, 100000)) + '.json')
                dumpConfigToJSON(json_file, cmd, user_id, file_id, src_file, key)
                self.__SendInfoToFileServer(json_file, server_ip, server_port)
                try:
                    if (os.path.exists(src_file) and os.path.isfile(src_file)):
                        os.remove(src_file)
                    if (os.path.exists(path) and os.path.isdir(path)):
                        root_dir = self.gui.FileManager.files_folder.defaultDir
                        fileInFolder = len(os.walk(path).next()[2])
                        if fileInFolder == 0:
                            for root, dirs, files in os.walk(path):
                                for name in dirs:
                                    path_to_folder = os.path.join(root, name)
                                    if len(os.walk(path_to_folder).next()[2]) == 0:
                                        if os.path.exists(path_to_folder):
                                            shutil.rmtree(path_to_folder)
                                if root != root_dir:
                                    parentDir = self.gui.FileManager.files_folder.getParentDir(root)
                                    if self.gui.FileManager.files_folder.currentDir == root:
                                        self.gui.FileManager.files_folder.currentDir = parentDir
                                    os.chdir(parentDir)
                                    if os.path.exists(root) and len(os.walk(root).next()[2]) == 0:
                                        shutil.rmtree(root)
                except IOError:
                    pass
                except OSError:
                    pass
                evt = UpdateFileListCtrlEvent()
                wx.PostEvent(self.gui, evt)

        for cmd, name, path, file_id, servers in data['deleted_files']:
            threads.deferToThread(defferedDeleteFile, data['user_id'], cmd, name, path, file_id, servers)
        del data['deleted_files']
        del data['user_id']

    def __RENF(self, event):
        """
            Rename file or folder and contains in him files
        """
        selectedItems = self.gui.FileManager.files_folder.getSelectedItems()
        if len(selectedItems) != 1:
            wx.MessageBox("For renaming necessary choose file or directory!", "Message")
        else:
            try:
                rnm_files = []
                currentDir = self.gui.FileManager.files_folder.currentDir
                defaultDir = self.gui.FileManager.files_folder.defaultDir
                filename = os.path.splitext(selectedItems[0])[0]
                dlg = InputDialog(self.gui.FileManager, -1, "Enter new file name or directory",
                                  self.gui.FileManager.ico_folder, RenameValidator(), filename)
                if dlg.ShowModal() == wx.ID_OK:
                    file_path = currentDir + selectedItems[0]
                    if os.path.isfile(file_path):
                        path, file = os.path.split(file_path)
                        file_hash, size = md5_for_file(file_path)
                        file_name_part = os.path.splitext(file)
                        file_name_part = (dlg.result, file_name_part[1])
                        new_filename = ''.join(file_name_part)
                        path = new_path = currentDir.replace(defaultDir, '')
                        rnm_files.append((file, path, file_hash, new_filename, new_path))
                        os.rename(currentDir+file, currentDir+new_filename)
                    elif os.path.isdir(file_path):
                        file_path += '/'
                        file_path_lst = filter(lambda item: item != '', file_path.split('/'))
                        new_folder_lst = file_path_lst[:]
                        new_folder_lst[-1] = dlg.result
                        new_folder_path = '/' + '/'.join(new_folder_lst) + '/'
                        for root, subdir, files in os.walk(file_path):
                            for filename in files:
                                file_in_folder_path = os.path.join(root, filename)
                                file_hash, size = md5_for_file(file_in_folder_path)
                                old_folder, name = os.path.split(file_in_folder_path)
                                new_folder = filter(lambda item: item != '', old_folder.split('/'))
                                new_folder[len(file_path_lst)-1] = dlg.result

                                backup = new_folder_lst[:]
                                if len(new_folder) > len(new_folder_lst):
                                    for elem_path in xrange(len(new_folder_lst), len(new_folder)):
                                        backup.append(new_folder[elem_path])

                                full_new_folder = '/' + '/'.join(backup) + '/'
                                full_new_folder = full_new_folder.replace(defaultDir, '')
                                full_old_folder = old_folder.replace(defaultDir, '') + '/'
                                rnm_files.append((filename, full_old_folder, file_hash, filename, full_new_folder))
                        os.rename(file_path, new_folder_path)
                    data = dumps({'cmd': 'RENF', 'user': self.login, 'auth': True, 'error': [], 'rename_files': rnm_files})
                    self.sendMessage(data, sync=True)
            except OSError:
                wx.MessageBox("File or directory with this name already exists!", "Message")

    def __CREN(self, data):
        wx.MessageBox("Task success processed!", "Message")
        evt = UpdateFileListCtrlEvent()
        wx.PostEvent(self.gui, evt)

    def __CRLN(self, event):
        """
            Create link on file
        """
        selectedItems = self.gui.FileManager.files_folder.getSelectedItems()
        if len(selectedItems) != 1:
            wx.MessageBox("For creating shared link necessary choose file!", "Error")
        else:
            key = self.gui.FileManager.options_frame.getCryptoKey()
            defaultDir = self.gui.FileManager.files_folder.defaultDir
            currentDir = self.gui.FileManager.files_folder.currentDir
            path = os.path.normpath(currentDir + selectedItems[0])
            if os.path.isfile(path):
                relative_path = currentDir.replace(defaultDir, "")
                file_hash, size = md5_for_file(path)
                file_info = (selectedItems[0], file_hash, relative_path, key)
                data = constructDataClient('CRLN', self.login, '', True, error='',
                                           file_info=file_info, description='')
                self.sendMessage(data)
            else:
                wx.MessageBox("For creating shared link necessary choose file!", "Error")

    def __CCLN(self, data):
        """
            Showing for user him created link (of course, if previous operation successfull)
        """
        if data['url'] is None:
            if data['error']:
                wx.MessageBox(data['error'][0], "Error")
            else:
                wx.MessageBox("Probably, you're tried create link on file, which not written on file servers yet."
                              "\nWrite him and try again.", "Error")
        else:
            wx.MessageBox("Your link on the file:\n{0}".format(data['url']), "Message")
        del data['error']
        del data['url']

    def __LINK(self, event):
        """
            Send request for download file by link
        """
        dlg = InputLink(self.gui.FileManager, -1, "Enter shared link", self.gui.FileManager.ico_folder)
        if dlg.ShowModal() == wx.ID_OK:
            data = constructDataClient('LINK', self.login, '', True, error='', url=dlg.result)
            self.sendMessage(data)

    def __CLNK(self, data):
        """
            Downloading file by link from another file storage
        """
        tmp_dir = self.gui.FileManager.options_frame.tmpFolder

        def defferedDownloadByLink(user_id, save_in, filename, file_id, key, server):
            src_file = os.path.normpath(save_in + '/' + filename)
            server_ip = str(server[0][0])
            server_port = str(server[0][1])
            json_file = os.path.normpath(tmp_dir + '/fsc_link_' + self.login + '_' + filename + '_' + str(randint(0, 100000)) + '.json')
            dumpConfigToJSON(json_file, "READU_FILE", user_id, file_id, src_file, key)
            self.__SendInfoToFileServer(json_file, server_ip, server_port)
            wx.MessageBox("File downloading {0} has completed!".format(filename), "Message")

        file_info = data.get('file_info', None)
        if file_info:
            file_id, filename, key, server = file_info
            if file_id and filename and key and server:
                dlg = wx.DirDialog(self.gui, "Choose directory for saving file", style=wx.DD_DEFAULT_STYLE)
                if dlg.ShowModal() == wx.ID_OK:
                    save_in = dlg.GetPath()
                    threads.deferToThread(defferedDownloadByLink, data['user_id'], save_in, filename, file_id, key, server)
            else:
                wx.MessageBox("Incorrect link or file has deleted!", "Error")
            del data['user_id']
            del data['file_info']
        else:
            wx.MessageBox("Incorrect link or file has deleted!", "Error")

    def __REPF(self, event):
        """
            Replace files/folder to another folder
        """
        currentDir = self.gui.FileManager.files_folder.currentDir
        defaultDir = self.gui.FileManager.files_folder.defaultDir
        selectedItems = self.gui.FileManager.files_folder.getSelectedItems()
        if len(selectedItems) == 0:
            wx.MessageBox("For renaming necessary choose file or directory!", "Message")
        else:
            dlg = wx.DirDialog(self.gui, "Choose directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                # move files to another folder at user disk
                replaceToFolder = os.path.normpath(dlg.GetPath()) + '/'
                if defaultDir not in replaceToFolder:
                    for item in selectedItems:
                        path_to_file = currentDir + item
                        path_to_file_new = replaceToFolder + item
                        shutil.move(path_to_file, path_to_file_new)
                    self.__CREP(None)
                # move files inside user's folder
                else:
                    rnm_files = []
                    for item in selectedItems:
                        path_to_file = currentDir + item
                        path_to_file_new = replaceToFolder + item
                        if os.path.isfile(path_to_file):
                            path, file = os.path.split(path_to_file)
                            file_hash, size = md5_for_file(path_to_file)
                            file_name_part = os.path.splitext(file)
                            new_filename = ''.join(file_name_part)
                            path = currentDir.replace(defaultDir, '')
                            new_path = replaceToFolder.replace(defaultDir, '')
                            rnm_files.append((file, path, file_hash, new_filename, new_path))
                            shutil.move(path_to_file, path_to_file_new)
                        elif os.path.isdir(path_to_file):
                            file_path = path_to_file + '/'
                            file_path_lst = filter(lambda item: item != '', file_path.split('/'))
                            new_folder_lst = filter(lambda item: item != '', path_to_file_new.split('/'))
                            new_folder_path = '/' + '/'.join(new_folder_lst) + '/'
                            for root, subdir, files in os.walk(file_path):
                                for filename in files:
                                    file_in_folder_path = os.path.join(root, filename)
                                    file_hash, size = md5_for_file(file_in_folder_path)
                                    old_folder, name = os.path.split(file_in_folder_path)
                                    new_folder_lst = filter(lambda item: item != '', path_to_file_new.split('/'))
                                    full_new_folder = '/' + '/'.join(new_folder_lst) + '/'
                                    full_new_folder = full_new_folder.replace(defaultDir, '')
                                    full_old_folder = old_folder.replace(defaultDir, '') + '/'
                                    rnm_files.append((filename, full_old_folder, file_hash, filename, full_new_folder))
                                    os.rename(file_path, new_folder_path)
                    data = dumps({'cmd': 'RENF', 'user': self.login, 'auth': True, 'error': [], 'rename_files': rnm_files})
                    self.sendMessage(data, sync=True)
            dlg.Destroy()

    def onUpdateListCtrl(self, event):
        self.gui.FileManager.files_folder.showFilesInDirectory(self.gui.FileManager.files_folder.currentDir)

    # there will be onRightClick method, which shows popup menu for clicked
    # on element in FileListCtrl
    # def onRightClick(self, event):

    def onOpen(self):
        self.factory._proto = self
        self.gui = self.factory._app._frame
        self.initBindings()

    def onMessage(self, payload, isBinary):
        self.gui.PreloaderStop()
        data = loads(payload)
        if data['cmd'] in self.commands.keys():
            self.commands[data['cmd']](data)

    def onClose(self, wasClean, code, reason):
        self.factory._proto = None
        self.gui = None


class GUIClientFactory(WebSocketClientFactory):

    protocol = GUIClientProtocol

    def __init__(self, url, app):
        WebSocketClientFactory.__init__(self, url)
        self._app = app
        self._proto = None


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-i", "--ip", dest = "ip", help = "The WebSocket IP", default = "localhost")
    parser.add_option("-p", "--port", dest = "port", help = "The WebSocket port", default = "9000")
    (options, args) = parser.parse_args()

    app = wx.App(0)
    app._factory = None
    app._frame = CloudStorage(None, -1, 'Log In', './gui/')
    reactor.registerWxApp(app)
    host_url = "wss://%s:%s" % (options.ip, options.port)
    app._factory = GUIClientFactory(host_url, app)

    # SSL client context: using default
    if app._factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(app._factory, contextFactory)
    reactor.run()
