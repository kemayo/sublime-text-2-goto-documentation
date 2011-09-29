#!/usr/bin/python

import os
import sublime
import sublime_plugin

def open_url(url):
    sublime.active_window().run_command('open_url', {"url": url})

class GotoDocumentationCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			word = self.view.word(region)
			if not word.empty():
				# scope is, e.g. "text.html.basic source.php.embedded.block.html keyword.other.new.php"
				scope = self.view.scope_name(word.begin()).strip()
				extracted_scope = scope.rpartition('.')[2]
				keyword = self.view.substr(word)
				getattr(self, '%s_doc' % extracted_scope, self.unsupported)(keyword, scope)
	
	def unsupported(self, keyword, scope):
		sublime.status_message("This scope is not supported: %s" % scope.rpartition('.')[2])
	
	def php_doc(self, keyword, scope):
		open_url("http://php.net/%s" % keyword)
