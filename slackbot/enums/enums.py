from enum import Enum

class GoogleAPI(Enum):
    YOUTUBE = "youtube"
    GMAIL   = "gmail"

class GmailFlag(Enum):
    READ = "read"
    UNREAD = "unread"
    ALL = "all"
    NONE = "none"