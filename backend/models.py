from pydantic import BaseModel
# Request models for the API endpoints
class Normativa(BaseModel):
    id: str
    name: str
    text: str
    summary: str
    organism: str
    state: str
    year: int
    normtype: str
    number: int
    read_count: int
    slug: str
    gazette: str

class Query(BaseModel):
    query: str
