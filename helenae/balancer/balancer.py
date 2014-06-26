from base_balancer import BaseBalancer


class Balancer(BaseBalancer):
    """
        This balancer using for distribute files between "File Servers"
        After getting request for read/write some file(s) this component finding ALL on-line "File servers" by plan:
            1) get list of all servers (get as parameter from main server)
            2) offline? -> delete from temporary list of on-line servers
            3) busy? -> delete from temporary list of busy servers (because busy == not available)
            4) after polling all servers -> random choise from list and return to main server response
                as tuple (IP, PORT)
    """
    def __init__(self):
        super(Balancer, self).__init__()
        self.handlers = self.__initHandlersUser()

    def __initHandlersUser(self):
        """
            Initialize handlers for every command
        """
        handlers = {}
        handlers['WRTE'] = self.__returnRandomServer
        handlers['READ'] = self.__returnRandomServer
        handlers['DELT'] = self.__returnRandomServer
        handlers['SYNC'] = self.__returnRandomServer
        return handlers

    def __deleteOffline(self):
        """
            Deleting from temporary list offline servers
        """
        self.lstFS = filter(lambda data: data[2] != 'OFFLINE', self.lstFS)

    def __deleteBusy(self):
        """
            Deleting from temporary list all servers at busy state
        """
        self.lstFS = filter(lambda data: data[2] != 'BUSY', self.lstFS)

    def __returnRandomServer(self, hash_file):
        """
            Random choise from list
        """
        return int(hash_file, 16) % len(self.lstFS)

    def updateFileServerList(self, lstFS):
        self.lstFS = lstFS

    def getFileServer(self, operation, hash_file):
        """
            Checking all servers and return main server response: "File server" params as tuple (IP, PORT)
        """
        self.__deleteOffline()
        self.__deleteBusy()
        if operation in self.handlers.keys() and len(self.lstFS) > 0:
            server_id = self.handlers[operation](hash_file)
            return (self.lstFS[server_id][0], self.lstFS[server_id][1])
        else:
            return None
