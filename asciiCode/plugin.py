# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matevž Pogačar (matevz.pogacar@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307, USA.

import os
from gi.repository import GObject, Gdk, Gtk, Gedit, PeasGtk
from xml.etree import ElementTree


class AsciiCode(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
	__gtype_name__ = "AsciiCode"
	window = GObject.property(type=Gedit.Window)

	filePath = ''
	disType = 16

	def __init__(self):
		GObject.Object.__init__(self)
		self.filePath = os.path.expanduser('~') + "/.local/share/gedit/plugins/asciiCode/config.xml"
		et = ElementTree.parse(self.filePath)

		disType = int(et.find("distype").text)
		if disType == 16 or disType == 10:
			self.disType = disType

	def do_activate(self):
		self.kpe_handler = self.window.connect('key-release-event', self.on_key_click)

	def do_deactivate(self):
		pass

	def do_update_state(self):
		pass

	def on_key_click(self, widget, event):
		view = self.window.get_active_view()
		buff = view.get_buffer()
		at_cursor = buff.get_iter_at_mark(buff.get_insert())
		c = buff.get_property('cursor-position')
		ic = buff.get_iter_at_offset(c)

		char = ic.get_char()
		ascii = self.get_ascii_code(char)
		display = '[NO CHAR]'
		if ascii != None:
			display = self.assemble_display(char, ascii)
		self.put_on_statusbar(display)

	def get_ascii_code(self, char):
		if char == "" or char == None:
			return None
		ascii = ord(char)
		return ascii

	def assemble_display(self, char, ascii):
		if ascii == 10:
			char = "\\n"
		elif ascii == 9:
			char = "\\t"
		elif ascii == 32:
			char = "[SPACE]"

		if self.disType==16:
			ascii = hex(ascii)
		content = char + ": " + str(ascii)
		return content

	def put_on_statusbar(self, content):
		statusbar = self.window.get_statusbar()
		message_id = statusbar.push(2, content)


	#When user calls configuration dialog (via Edit->Preferences->Plugins).
	def do_create_configure_widget(self):
		widget = Gtk.VButtonBox()
		rb1 = Gtk.RadioButton.new_with_label_from_widget(None, "Decimal")
		rb2 = Gtk.RadioButton.new_from_widget(rb1)
		rb2.set_label("Hexadecimal")
		widget.add(rb1)
		widget.add(rb2)
		rb1.connect("toggled", self.callback, "10")
		rb2.connect("toggled", self.callback, "16")
		if self.disType==16:
		    rb2.set_active(True)
		else:
		    rb1.set_active(True)
		return widget

	def callback(self, widget, data=None):
		et = ElementTree.parse(self.filePath)

		position_xml = et.find("distype")
		position_xml.text = str(int(data))
		et.write(self.filePath)
		self.disType = data
