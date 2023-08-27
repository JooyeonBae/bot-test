from typing import Dict, Any

GoogleAPIDict: Dict[str, Dict[str, Any]] = {
    "youtube": {
        "scopes": ['https://www.googleapis.com/auth/youtube.force-ssl'],
        "version": "v3",
    },
    "gmail":{
        "scopes":['https://www.googleapis.com/auth/gmail.readonly'],
        "version":'v1',
    }
}

blockable_emails = ['amazon@gmail.com']
