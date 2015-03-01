"""
    This module contains basics commands, which [user/file server] can using
"""

commands_user = {
      "AUTH": "autorization with server"
    , "READ": "read some file from storage"
    , "WRTE": "write file into storage"
    , "DELT": "delete file from storage"
    , "RNME": "rename file"
    , "LIST": "get list of all files from storage with this user"
    , "SYNC": "synchronize files with storage on the server"
    , "CRLN": "create link for file"
    , "LINK": "download file by link"
    , "EXIT": "disconnect from server or end session"
}

commands_server = {
      "AUTH": "autorization with server"
    , "READ": "read some file from storage"
    , "WRTE": "write file into storage"
    , "DELT": "delete file from storage"
    , "RNME": "rename file"
    , "LIST": "get list of all files from storage with this user"
    , "SYNC": "synchronize files with storage on the server"
    , "CRLN": "create link for file"
    , "LINK": "download file by link"
    , "EXIT": "disconnect from server or end session"
    # commands for GUI app
    , "WRTF": "massive write files into storage"
    , "REAF": "massive read files from storage"
    , "RENF": "massive rename files"
    , "DELF": "massive delete files from storage"
    , "REPF": "replace files"
    , "GETF": "getting all file info for GUI app"
    , "LGUI": "download file by user link"
}

commands_handlers_user   = dict((key, None) for key in commands_user.keys())
commands_handlers_server = dict((key, None) for key in commands_server.keys() if key not in ('AUTH', 'EXIT'))