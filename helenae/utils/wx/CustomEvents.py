import  wx.lib.newevent

# Custom event for updating FileListCtrl, which will be called by some other thread in Twisted event-loop
UpdateFileListCtrlEvent, EVT_UPDATE_FILE_LIST_CTRL = wx.lib.newevent.NewEvent()