from spaceone.core.pygrpc.server import GRPCServer
from .repository import Repository
from .plugin import Plugin
from .dashboard_template import DashboardTemplate


_all_ = ['app']

app = GRPCServer()
app.add_service(Repository)
app.add_service(Plugin)
app.add_service(DashboardTemplate)
