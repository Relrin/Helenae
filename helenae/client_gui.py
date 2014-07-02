"""
    Implementation of GUI client for Helenae project.
    At this file, as you can see, written wrapper for GUI, which founded in /gui/ folder.
    For UI using only wxPython. Also "patched" twisted event-loop for support event-loop from wxPython
"""
import wx
from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from gui.filemanager import CloudStorage

# TODO: Add event handlers for Twisted
# TODO: Add login/registration/options/about window

class GUIClientProtocol(WebSocketClientProtocol):

    gui = None

    def onOpen(self):
        self.factory._proto = self
        self.gui = self.factory._app._frame
        self.gui.Show()

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
    app = wx.App(False)
    app._factory = None
    app._frame = CloudStorage(None, -1, 'CloudStorage')
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