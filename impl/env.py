import os

token = os.environ.get("mrvn_token", None)
extension_dirs = os.environ.get("mrvn_extension_dirs", "extensions").split(",")
debug = os.environ.get("mrvn_debug", None)
debug_guilds = [int(x) for x in os.environ.get("mrvn_debug_guilds", "").split(",") if x.isdigit()]
