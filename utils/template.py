# --------------------------------------------------
from .reloading import ReloadModule
class RM(ReloadModule):
    @classmethod
    def reload_mod(cls):
        # importer les modules
        cls.reload("les modules")
RM.reload()
# --------------------------------------------------