
from .simple_tags import StandaloneTag

class ViteDev(StandaloneTag):
    tags = {"vite_dev"}

    def __init__(self, environment):
        super().__init__(environment)
        # environment.extend(vite_metadata_prefix="", vite_metadata=None)
        environment.extend(vite_dev_mod_prefix="", vite_dev_mode=None)
        environment.extend(vite_dev_server_prefix="", vite_dev_server=None)

    def render(self, script_name="main.js"):
        _url = f"{self.environment.vite_dev_server}/{script_name}"
        if self.environment.vite_dev_mode:
            return f"""<script type="module" src="{_url}"></script>"""


class ViteAsset(StandaloneTag):
    tags = {"vite_asset"}

    def __init__(self, environment):
        super().__init__(environment)
        # environment.extend(vite_metadata_prefix="", vite_metadata=None)
        environment.extend(vite_manifest_prefix="", vite_manifest=None)
        environment.extend(vite_dev_mod_prefix="", vite_dev_mode=None)
        environment.extend(vite_static_url_prefix="", vite_static_url=None)

    def render(self, asset_name="main.js"):
        if not self.environment.vite_dev_mode:
            asset = self.environment.vite_manifest[asset_name]["file"]
            return f"""<script type="module" src="{asset}"></script>"""
