import wx
import pytest

from helpers.Faker import Faker
from fixtures.wxPython import wxMainApp

from helenae.gui.CloudStorage import ID_BUTTON_CANCEL, ID_BUTTON_ACCEPT, ID_NEW_MEMBER_TXT
from helenae.gui.widgets.RegisterCtrl import ID_BUTTON_EXIT, ID_BUTTON_REG
from helenae.gui.widgets.Filemanager import ID_EXIT
from helenae.gui.widgets.CompleteRegCtrl import ID_BUTTON_CLOSE_MSG


@pytest.mark.parametrize("login, password", [
    ("relrin", "123456"),
    (" r e   lr  in ", " 12  3 4 5 6"),
    (" r  elrin", " 1 2 3 4 56    "),
    (" re l rin  ", " 123456"),
    (" rel r i     n", " 1 2 3 4 5 6 "),
    (" r e l r i n", "    123456"),
    ("  rel rin  ", "  123 45 6"),
])
def test_login_successful(wxMainApp, login, password):
    Faker.enterFakeLogin(wxMainApp, login, password)
    Faker.clickButton(wxMainApp, ID_BUTTON_ACCEPT)
    Faker.clickButton(wxMainApp.FileManager, ID_EXIT)


@pytest.mark.parametrize("login, password", [
    pytest.mark.xfail(("", "123456")),
    pytest.mark.xfail(("   ", "123456")),
    pytest.mark.xfail(("rel", "")),
    pytest.mark.xfail(("rel", "      ")),
    pytest.mark.xfail(("rel", "12 345")),
])
def test_login_failed(wxMainApp, login, password):
    Faker.enterFakeLogin(wxMainApp, login, password)
    wx.CallAfter(Faker.clickButtonDialogOK(wxMainApp))
    Faker.clickButton(wxMainApp, ID_BUTTON_ACCEPT)
    Faker.clickButton(wxMainApp, ID_BUTTON_CANCEL)


@pytest.mark.parametrize("login, password, fullname, email", [
    ("testuser", "123456", "Im test user", "test@mail.com"),
    (" test user", "123456", "Im test user", "test@mail.com"),
    (" test user ", "123456", "Im test user", "test@mail.com"),
    ("test user", "123456", "Im test user", "test@mail.com"),
    ("   test   user  ", "123456", "Im test user", "test@mail.com"),
    (" te st u ser", "123456", "Im test user", "test@mail.com"),
    ("testuser", "1234 56", "Im test user", "test@mail.com"),
    ("testuser", "1 234 56   ", "Im test user", "test@mail.com"),
    ("testuser", " 1234 56", "Im test user", "test@mail.com"),
    ("testuser", "1 2 3 4 5 6", "Im test user", "test@mail.com"),
    ("testuser", "  1 2 34   56   ", "Im test user", "test@mail.com"),
    ("testuser", "  1 23 4     56", "Im test user", "test@mail.com"),
    ("testuser", "123456", "Im   test  user   ", "test@mail.com"),
    ("testuser", "123456", "  Im  test user", "test@mail.com"),
    ("testuser", "123456", "Im  test  user  ", "test@mail.com"),
    ("testuser", "123456", " Im test user  ", "test@mail.com"),
    ("testuser", "123456", "Im test   user", "test@mail.com"),
])
def test_registration_successful(wxMainApp, login, password, fullname, email):
    """
        Trying to enter invalid login in registration form
        (typing logins with errors, but out app fix this to valid)
    """
    Faker.clickHyperlink(wxMainApp, ID_NEW_MEMBER_TXT)
    Faker.enterFakeRegisterData(wxMainApp.RegisterWindow, login, password, fullname, email)
    Faker.clickButton(wxMainApp.RegisterWindow, ID_BUTTON_REG)
    Faker.clickButton(wxMainApp, ID_BUTTON_CLOSE_MSG)


@pytest.mark.parametrize("login,password,fullname, email", [
    pytest.mark.xfail(("", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail((" ", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("  ", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail((" t e ", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail((" t   e", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail((" t  e", "123456", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", "", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", " ", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", "      ", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", " 1    ", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123 56", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", "  12    45   6", "Im test user", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123456", "", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123456", "     ", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123456", " Im te  ", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123456", "   Im    te ", "test@mail.com")),
    pytest.mark.xfail(("testuser", "123456", " I m. e  ", "test@mail.com")),
])
def test_registration_failed(wxMainApp, login, password, fullname, email):
    """
        Trying to enter invalid password in registration form
        (typing password with errors, but out app fix this to valid)
    """
    Faker.clickHyperlink(wxMainApp, ID_NEW_MEMBER_TXT)
    Faker.enterFakeRegisterData(wxMainApp.RegisterWindow, login, password, fullname, email)
    wx.CallAfter(Faker.clickButtonDialogOK(wxMainApp.RegisterWindow))
    Faker.clickButton(wxMainApp.RegisterWindow, ID_BUTTON_REG)
    Faker.clickButton(wxMainApp, ID_BUTTON_CLOSE_MSG)


def test_close_1(wxMainApp):
    """
        Close login window, on clicking "Cancel"
    """
    Faker.clickButton(wxMainApp, ID_BUTTON_CANCEL)


def test_close_2(wxMainApp):
    """
        Close application by scheme:
            1) open main window
            2) go to registration
            3) close registration window
    """
    Faker.clickHyperlink(wxMainApp, ID_NEW_MEMBER_TXT)
    Faker.clickButton(wxMainApp, ID_BUTTON_EXIT)


def test_close_3(wxMainApp):
    """
        Close application by scheme:
            1) open main window
            2) auth with fake account
            3) click on button "F10 Exit"
    """
    Faker.enterFakeLogin(wxMainApp, "relrin", "123456")
    Faker.clickButton(wxMainApp, ID_BUTTON_ACCEPT)
    Faker.clickButton(wxMainApp.FileManager, ID_EXIT)


def test_close_4(wxMainApp):
    """
        Close application by scheme:
            1) open main window
            2) auth with fake account
            3) click on "File" -> "Exit"
    """
    Faker.enterFakeLogin(wxMainApp, "relrin", "123456")
    Faker.clickButton(wxMainApp, ID_BUTTON_ACCEPT)
    Faker.clickMenuItem(wxMainApp.FileManager, ID_EXIT)

