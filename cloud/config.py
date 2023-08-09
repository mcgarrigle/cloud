import os

class Config:

    @staticmethod
    def xdg_config_home():
        return os.environ.get('XDG_CONFIG_HOME',None) or os.path.join(os.environ['HOME'], ".config")

    @staticmethod
    def cloud_config_path():
        path1 = os.path.join(Config.xdg_config_home(), "cloud", "user-data")
        path2 = os.path.join(os.environ['HOME'], ".cloud_config")
        for path in [ path1, path2 ]:
          if os.path.isfile(path):
              return path
        return os.path.join(ROOT, "metadata", "user-data")
