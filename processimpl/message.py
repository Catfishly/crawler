class Message:
    REQUEST_GET = 1
    REQUEST_LOG = 2
    msg_types = [REQUEST_GET, REQUEST_LOG]

    def __init__(self, mtype, mdata):
        assert mtype in Message.msg_types
        self.mtype = mtype
        self.mdata = mdata

    def gettype(self):
        return self.mtype

    def getdata(self):
        return self.mdata
