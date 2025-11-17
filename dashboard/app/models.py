# app/models.py
from pydantic import BaseModel

class ServerConfig(BaseModel):
    id: str
    label: str
    base_url: str
    type: str = "remote"
    role: str = "client"  # "client" 또는 "central"
    tls: bool = False

class ContainerAction(BaseModel):
    node_id: str
    container_id: str

