from . import _
from Plugins.Plugin import PluginDescriptor
from Crypto.Cipher import AES

def broadlinkMain(session, **kwargs):
	import ui
	session.open(ui.broadlink, plugin_path)

def Plugins(path,**kwargs):
	global plugin_path
	plugin_path = path
	result = [PluginDescriptor(name="E-BroadLink",description=_("Production BroadLink management"),where=[ PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU ],icon='plugin.png',fnc=broadlinkMain)]
	return result
