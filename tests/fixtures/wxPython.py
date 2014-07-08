# -*- coding: utf-8 -*-
import os
import wx
import pytest

from helenae.gui.CloudStorage import CloudStorage, ID_BUTTON_ACCEPT
from helenae.gui.widgets.RegisterCtrl import ID_BUTTON_REG
from helenae.gui.widgets.Filemanager import ID_EXIT
from helenae.gui.widgets.CompleteRegCtrl import ID_BUTTON_CLOSE_MSG

@pytest.yield_fixture(scope="function", autouse=True)
def wxMainApp():
    app = wx.App(False)

    def initBindings(frame):

        def FakeAuth(event):
            app._frame.ClearErrorsLabels()
            if app._frame.login_input.GetValidator().Validate(app._frame.login_input) and \
                app._frame.pass_input.GetValidator().Validate(app._frame.pass_input):
                app._frame.PreloaderPlay()
                login = app._frame.login_input.GetValue().strip()
                password = app._frame.pass_input.GetValue().strip()
                assert login == 'relrin'
                assert password == '123456'
                app._frame.Hide()
                app._frame.FileManager.Show()

        def FakeRegistration(event):
            app._frame.RegisterWindow.ClearErrorsLabels()
            if app._frame.RegisterWindow.login_input.GetValidator().Validate(app._frame.RegisterWindow.login_input) and \
                    app._frame.RegisterWindow.pass_input.GetValidator().Validate(app._frame.RegisterWindow.pass_input) and \
                    app._frame.RegisterWindow.fullname_input.GetValidator().Validate(app._frame.RegisterWindow.fullname_input):
                app._frame.RegisterWindow.PreloaderPlay()
                login = app._frame.RegisterWindow.login_input.GetValue().strip()
                password = app._frame.RegisterWindow.pass_input.GetValue().strip()
                fullname = app._frame.RegisterWindow.fullname_input.GetValue().strip()
                email = app._frame.RegisterWindow.email_input.GetValue().strip()
                assert login == 'testuser'
                assert password == '123456'
                assert fullname == 'Im test user'
                assert email == 'test@mail.com'
                app._frame.RegisterWindow.msg_box.Show()

        def FakeCompleteRegister(event):
            app._frame.RegisterWindow.Hide()
            app._frame.Close()
            app._frame.RegisterWindow.Close()

        def FakeExit(event):
            app._frame.Close()
            app._frame.RegisterWindow.Close()
            app._frame.FileManager.Close()

        frame.Bind(wx.EVT_BUTTON, FakeAuth, id=ID_BUTTON_ACCEPT)
        frame.Bind(wx.EVT_BUTTON, FakeRegistration, id=ID_BUTTON_REG)
        frame.Bind(wx.EVT_MENU, FakeExit, id=ID_EXIT)
        frame.Bind(wx.EVT_BUTTON, FakeExit, id=ID_EXIT)
        frame.Bind(wx.EVT_BUTTON, FakeCompleteRegister, id=ID_BUTTON_CLOSE_MSG)

    pathIconsFolder = os.path.abspath('..') + '/helenae/gui'
    app._frame = CloudStorage(None, -1, 'Testing wxPython app', pathIconsFolder)
    initBindings(app._frame)
    app._frame.Show()
    yield app._frame
    app._frame.Close()
    app.MainLoop()
