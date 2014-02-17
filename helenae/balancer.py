class Balancer(object):
    """
        This balancer using for distribute files between "File Servers"
        After getting request for read/write some file(s) this component finding ALL on-line "File servers" by plan:
            1) get list of all servers (get as parameter from main server)
            2) offline? -> delete from temporary list of on-line servers
            3) busy? -> delete from temporary list of on-line servers (because busy == not available)
            4) online and not using? -> reserve at "File Servers" list
                4.1) but if didnt he have free space for our file -> delete from list
            5) after polling all servers -> random choise from list and return to main server response
                as tuple (IP, PORT)
    """
    def __init__(self):
        pass

    def __deleteOffline(self):
        """
            Deleting from temporary list offline servers
        """
        pass

    def __deleteBusy(self):
        """
            Deleting from temporary list all servers at busy state
        """
        pass

    def __checkOnline(self):
        """
            Reserve at temporary list all on-line servers (which not using), but have free space
        """
        pass

    def __returnRandomServer(self):
        """
            Random choise from list
        """
        pass

    def getFileServer(self):
        """
            Checking all servers and return main server response: "File server" params as tuple (IP, PORT)
        """
        pass