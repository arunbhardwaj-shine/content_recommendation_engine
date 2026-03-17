from pydantic import BaseModel, HttpUrl

class UrlRequest(BaseModel):
    url: HttpUrl
    top_k: int = 3