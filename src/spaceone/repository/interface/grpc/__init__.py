from spaceone.core.pygrpc.server import GRPCServer
from .repository import Repository
from .plugin import Plugin


_all_ = ['app']

app = GRPCServer()
app.add_service(Repository)
app.add_service(Plugin)
