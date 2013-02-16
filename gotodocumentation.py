#!/usr/bin/python

import functools
import os
import re
import subprocess
import threading

import sublime
import sublime_plugin


def open_url(url):
    sublime.active_window().run_command('open_url', {"url": url})


def main_thread(callback, *args, **kwargs):
    # sublime.set_timeout gets used to send things onto the main thread
    # most sublime.[something] calls need to be on the main thread
    sublime.set_timeout(functools.partial(callback, *args, **kwargs), 0)


def _make_text_safeish(text, fallback_encoding):
    # The unicode decode here is because sublime converts to unicode inside
    # insert in such a way that unknown characters will cause errors, which is
    # distinctly non-ideal... and there's no way to tell what's coming out of
    # git in output. So...
    try:
        unitext = text.decode('utf-8')
    except UnicodeDecodeError:
        unitext = text.decode(fallback_encoding)
    return unitext


class CommandThread(threading.Thread):
    def __init__(self, command, on_done, working_dir="", fallback_encoding=""):
        threading.Thread.__init__(self)
        self.command = command
        self.on_done = on_done
        self.working_dir = working_dir
        self.fallback_encoding = fallback_encoding

    def run(self):
        try:
            # Per http://bugs.python.org/issue8557 shell=True is required to
            # get $PATH on Windows. Yay portable code.
            shell = os.name == 'nt'
            if self.working_dir != "":
                os.chdir(self.working_dir)

            proc = subprocess.Popen(self.command,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=shell, universal_newlines=True)
            output = proc.communicate()[0]
            # if sublime's python gets bumped to 2.7 we can just do:
            # output = subprocess.check_output(self.command)
            main_thread(self.on_done,
                _make_text_safeish(output, self.fallback_encoding))
        except subprocess.CalledProcessError as e:
            main_thread(self.on_done, e.returncode)


class GotoDocumentationCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            word = self.view.word(region)
            if not word.empty():
                # scope: "text.html.basic source.php.embedded.block.html keyword.other.new.php"
                scope = self.view.scope_name(word.begin()).strip()
                extracted_scope = scope.rpartition('.')[2]
                keyword = self.view.substr(word)
                getattr(self, '%s_doc' % extracted_scope, self.unsupported)(keyword, scope)

    def unsupported(self, keyword, scope):
        sublime.status_message("This scope is not supported: %s" % scope.rpartition('.')[2])

    def php_doc(self, keyword, scope):
        open_url("http://php.net/%s" % keyword)

    def rails_doc(self, keyword, scope):
        open_url("http://api.rubyonrails.org/?q=%s" % keyword)

    def controller_doc(self, keyword, scope):
        open_url("http://api.rubyonrails.org/?q=%s" % keyword)

    def ruby_doc(self, keyword, scope):
        open_url("http://api.rubyonrails.org/?q=%s" % keyword)

    def js_doc(self, keyword, scope):
        open_url("https://developer.mozilla.org/en-US/search?q=%s" % keyword)

    coffee_doc = js_doc

    def python_doc(self, keyword, scope):
        """Not trying to be full on intellisense here, but want to make opening a
        browser to a docs.python.org search a last resort
        """
        if not re.match(r'\s', keyword):
            self.run_command(["python", "-m", "pydoc", keyword])
            return

        open_url("http://docs.python.org/search.html?q=%s" % keyword)

    def clojure_doc(self, keyword, scope):
        open_url("http://clojuredocs.org/search?x=0&y=0&q=%s" % keyword)

    def go_doc(self, keyword, scope):
        open_url("http://golang.org/search?q=%s" % keyword)

    def smarty_doc(self, keyword, scope):
        open_url('http://www.smarty.net/%s' % keyword)

    def cmake_doc(self, keyword, scope):
        open_url('http://cmake.org/cmake/help/v2.8.8/cmake.html#command:%s' % keyword.lower())

    def run_command(self, command, callback=None, **kwargs):
        if not callback:
            callback = self.display_output
        thread = CommandThread(command, callback, **kwargs)
        thread.start()

    def display_output(self, output):
        if not hasattr(self, 'output_view'):
            self.output_view = sublime.active_window().get_output_panel("gotodocumentation")
        self.output_view.set_read_only(False)
        edit = self.output_view.begin_edit()
        region = sublime.Region(0, self.output_view.size())
        self.output_view.erase(edit, region)
        self.output_view.insert(edit, 0, output)
        self.output_view.end_edit(edit)
        self.output_view.set_read_only(True)
        sublime.active_window().run_command("show_panel", {"panel": "output.gotodocumentation"})
