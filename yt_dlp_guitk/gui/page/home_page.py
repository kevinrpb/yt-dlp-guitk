import guitk as ui

from ..components.simple_widget import SimpleWidget


class HomePage(SimpleWidget):
    def _create_layout(self):
        ui.Label("home")
