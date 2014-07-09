# -*- coding: utf-8 -*-
"""
    Implementation of GUI client for Helenae project.
    At this file, as you can see, written wrapper for GUI, which founded in /gui/ folder.
    For UI using only wxPython. Also "patched" twisted event-loop for support event-loop from wxPython
"""
from json import loads, dumps

import wx
from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from utils import commands
from gui.CloudStorage import CloudStorage, ID_BUTTON_ACCEPT
from gui.widgets.RegisterCtrl import ID_BUTTON_REG
from gui.widgets.CompleteRegCtrl import ID_BUTTON_CLOSE_MSG

# TODO: Add event handlers for Twisted
# TODO: Add login/registration/options/about window

class GUIClientProtocol(WebSocketClientProtocol):

    gui = None

    def __init__(self):
        self.commands = self.__initHandlers()

    def __initHandlers(self):
        handlers = {}
        # basic commands
        handlers['AUTH'] = self.__AUTH
        handlers['CREG'] = self.__CREG
        # continues operations...
        handlers['RAUT'] = self.__RAUT
        handlers['RREG'] = self.__RREG
        return handlers

    def initBindings(self):
        self.gui.Bind(wx.EVT_BUTTON, self.__StartAuth, id=ID_BUTTON_ACCEPT)
        self.gui.RegisterWindow.Bind(wx.EVT_BUTTON, self.__StartRegistration, id=ID_BUTTON_REG)
        self.gui.Bind(wx.EVT_BUTTON, self.onEndRegister, id=ID_BUTTON_CLOSE_MSG)

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
            data = commands.constructDataClient('AUTH', login, password, False)
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
            self.gui.FileManager.Show()

    def __RAUT(self, data):
        """
            Handler for re-auth command, if incorrect user/password or something else...
        """
        for error_msg in data['error']:
            if 'User not found' in error_msg:
                self.gui.ShowErrorLogin('Такого пользователя не существует!')
            elif 'Incorrect password' in error_msg:
                self.gui.ShowErrorPassword('Неправильный пароль!')

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
                self.gui.RegisterWindow.ShowErrorLogin('Логин должен содержать минимум 3 символа!')
            if 'This user already exists' in error_msg:
                self.gui.RegisterWindow.ShowErrorLogin('Этот логин уже используется! Введите другой.')
            if 'Length of password was been more than 6 symbols!' in error_msg:
                self.gui.RegisterWindow.ShowErrorPassword('Пароль должен содержать минимум 6 символов!')
            if "Full name can't be empty!" in error_msg:
                self.gui.RegisterWindow.ShowErrorName('Это поле не может быть пустым!')

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
    app = wx.App(0)
    app._factory = None
    app._frame = CloudStorage(None, -1, 'Авторизация', './gui/')
    reactor.registerWxApp(app)
    host_url = "wss://%s:%s" % ("localhost", 9000)
    app._factory = GUIClientFactory(host_url, app)

    # SSL client context: using default
    if app._factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(app._factory, contextFactory)
    reactor.run()