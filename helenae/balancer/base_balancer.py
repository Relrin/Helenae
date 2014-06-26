from abc import abstractmethod

class BaseBalancer(object):
    """
        Basic class for balancers
    """
    def __init__(self):
        self.lstFS = []

    @abstractmethod
    def updateFileServerList(self, lstFS):
        """
            Updating list with servers
        """
        pass

    @abstractmethod
    def getFileServer(self, operation, hash_file):
        """
            This place is specially for all handlers, when server sended request as some command
        """
        pass