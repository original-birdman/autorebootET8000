from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.Screen import Screen
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, fileExists
import gettext
import os

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("Autoreboot", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/Autoreboot/locale/"))

def _(txt):
	t = gettext.dgettext("Autoreboot", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class Autoreboot(Screen):
	skin = """
	<screen position="center,center" size="500,40" title="Setup menu for et8000" >
		<widget name="menu" position="10,10" size="480,180" scrollbarMode="showOnDemand" />
	</screen>"""
	
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.menu = args
		list = []
		if fileExists("/etc/init.d/driver-et8000-fix"):
			list.append((_("Disable auto reboot"), "stop"))
		else:
			list.append((_("Enable auto reboot"), "start"))
		self["menu"] = MenuList(list)
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)
		self.setTitle(_("Setup menu for et8000"))

	def run(self):
		returnValue = self["menu"].l.getCurrentSelection()[1]
		if returnValue is not None:
			if returnValue == "start":
				self.setFile()
			elif returnValue == "stop":
				self.removeFile()

	def setFile(self):
		if not fileExists("/etc/init.d/driver-et8000-fix"):
			os.system("cp /usr/lib/enigma2/python/Plugins/SystemPlugins/Autoreboot/driver-et8000-fix /etc/init.d/driver-et8000-fix")
		if fileExists("/etc/init.d/driver-et8000-fix"):
			os.chmod("/etc/init.d/driver-et8000-fix", 0o755)
# Start early, so S07 in rcS.d
			os.system("update-rc.d driver-et8000-fix start 07 S . stop 99 6 .")
		self.close()
	
	def removeFile(self):
		os.system("update-rc.d -f driver-et8000-fix remove")
		os.system("rm -rf /etc/init.d/driver-et8000-fix")
		self.close()

def open_setup(session, **kwargs):
	session.open(Autoreboot)

def start_main(menuid, **kwargs):
	if menuid == "system":
		return [(_("Auto reboot et8000"), open_setup, "autoreboot_setup", None)]
	else:
		return []

def Plugins(**kwargs):
	from os import path
	if path.exists("/proc/stb/info/boxtype"):
		try:
			boxtype = open("/proc/stb/info/boxtype").read().strip()
		except:
			boxtype = ""
		if boxtype.startswith("et8000"):
			return [PluginDescriptor(name = "Auto reboot", where = PluginDescriptor.WHERE_MENU, fnc = start_main)]
	return []
