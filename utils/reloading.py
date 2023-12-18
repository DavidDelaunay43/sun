class ReloadModule:
    
    modules = None
    
    @classmethod
    def reload(cls): 
        pass
    
    @classmethod 
    def reload_mod(cls, *mods):
        from importlib import reload
        for mod in mods:
            reload(mod)