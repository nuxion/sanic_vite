from .simple_tags import StandaloneTag


class Static(StandaloneTag):
    tags = {"static"}

    def __init__(self, environment):
        super().__init__(environment)
        # environment.extend(vite_metadata_prefix="", vite_metadata=None)
        environment.extend(vite_dev_mod_prefix="", vite_dev_mode=None)
        environment.extend(vite_dev_server_prefix="", vite_dev_server=None)

    def render(self, script_name="main.js"):
        _url = f"{self.environment.vite_dev_server}/{script_name}"
        if self.environment.vite_dev_mode:
            return f"""<script type="module" src="{_url}"></script>"""
