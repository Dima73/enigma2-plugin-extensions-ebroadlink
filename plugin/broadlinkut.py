from __future__ import print_function
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from Components.Label import Label
import os
from xml.etree.cElementTree import parse as cet_parse


XML_BTAB = "/etc/enigma2/broadlink.xml"


class broadlinkUt(Screen):

	def __init__(self):
		self.remotepc = {}
		self.configActualized = False

		self.pcStr = _("BroadLink")

	def getRemotePCPoints(self):
		self.remotepc = {}

		if not os.path.exists(XML_BTAB):
			self.setDummyRecord()
			self.writePCsConfig()

		try:
			tree = cet_parse(XML_BTAB).getroot()
		except Exception as e:
			print("[broadlink  plugin] Error reading /etc/enigma2/broadlink.xml:", e)

		def getValue(definitions, default):
			ret = ""
			Len = len(definitions)
			return Len > 0 and definitions[Len - 1].text or default
		for pc in tree.findall("host"):
			data = {'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False}
			try:
				data['name'] = getValue(pc.findall("name"), self.pcStr).encode("UTF-8")
				data['ip'] = getValue(pc.findall("ip"), "192.168.1.0").encode("UTF-8")
				data['mac'] = getValue(pc.findall("mac"), "00:00:00:00:00:00").encode("UTF-8")
				data['system'] = getValue(pc.findall("system"), "0").encode("UTF-8")
				data['user'] = getValue(pc.findall("user"), "administrator").encode("UTF-8")
				data['passwd'] = getValue(pc.findall("passwd"), "password").encode("UTF-8")
				data['bqdn'] = getValue(pc.findall("bqdn"), "0").encode("UTF-8")
				self.remotepc[data['name']] = data
			except Exception as e:
				print("[broadlink] Error reading remotebroadlink:", e)

		self.checkList = self.remotepc.keys()
		if not self.checkList:
		# exists empty file => create dummy record
			self.setDummyRecord()

		self.checkList = self.remotepc.keys()
		if not self.checkList:
			print("\n[broadlink] self.remotepc without remotebroadlink", self.remotepc)
		else:
			self.checkList.pop()

	def setDummyRecord(self):
		data = {'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False}
		data['name'] = self.pcStr
		data['ip'] = "192.168.1.100"
		data['mac'] = "00:00:00:00:00:00"
		data['system'] = "0"
		data['user'] = "administrator"
		data['passwd'] = "password"
		data['bqdn'] = "0"
		self.remotepc[data['name']] = data

	def setRemotePCAttribute(self, pcpoint, attribute, value):
		if pcpoint in self.remotepc:
			self.remotepc[pcpoint][attribute] = value

	def getPCsList(self):
		self.getRemotePCPoints()
		return self.remotepc

	def writePCsConfig(self):
		list = ['<?xml version="1.0" ?>\n<broadlink>\n']

		for name, data in self.remotepc.items():
			list.append(' <host>\n')
			list.append(''.join(["  <name>", data['name'], "</name>\n"]))
			list.append(''.join(["  <ip>", data['ip'], "</ip>\n"]))
			list.append(''.join(["  <mac>", data['mac'], "</mac>\n"]))
			list.append(''.join(["  <system>", data['system'], "</system>\n"]))
			list.append(''.join(["  <user>", data['user'], "</user>\n"]))
			list.append(''.join(["  <passwd>", data['passwd'], "</passwd>\n"]))
			list.append(''.join(["  <bqdn>", data['bqdn'], "</bqdn>\n"]))
			list.append(' </host>\n')

		list.append('</broadlink>\n')

		file = None
		try:
			file = open(XML_BTAB, "w")
			file.writelines(list)
		except Exception as e:
			print("[broadlink plugin] Error Saving broadlink List:", e)
		finally:
			if file is not None:
				file.close()

	def removePC(self, pcpoint):
		self.newremotepc = {}
		for name, data in self.remotepc.items():
			if name.strip() != pcpoint.strip():
				self.newremotepc[name] = data
		self.remotepc.clear()
		self.remotepc = self.newremotepc


ibroadlinkUt = broadlinkUt()
