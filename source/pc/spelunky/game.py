from source.meta.gui.gamelib import GameParent

class Game(GameParent):
    def __init__(self, my_subpath=""):
        super().__init__(my_subpath)
        #FIXME: Do we want to translate the game's display name?
        self.name = "Spelunky"					#to be replaced by a name like "Super Metroid"
        self.console_name = "pc"				#to be replaced by the console name, e.g. "snes"
        self.internal_name = "spelunky"	#to be replaced by the specific folder name that this app uses, e.g. "metroid3"
