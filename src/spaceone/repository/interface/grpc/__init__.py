from spaceone.core.pygrpc.server import GRPCServer
from .repository import Repository
from .plugin import Plugin
from .schema import Schema
from .policy import Policy


_all_ = ['app']

app = GRPCServer()
app.add_service(Repository)
app.add_service(Plugin)
app.add_service(Schema)
app.add_service(Policy)
