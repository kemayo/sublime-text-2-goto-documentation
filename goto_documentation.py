# GotoDocumentation Sublime Plugin
# Jun 2014

import webbrowser
import sublime, sublime_plugin
import re, os
import subprocess

default_docs = {
        "ahk": "http://www.ahkscript.org/docs/commands/%(query)s.htm",
        "rails": "http://api.rubyonrails.org/?q=%(query)s",
        "controller": "http://api.rubyonrails.org/?q=%(query)s",
        "ruby": "http://ruby-doc.com/search.html?q=%(query)s",
        "js": "https://developer.mozilla.org/en-US/search?q=%(query)s&topic=js",
        "html": "https://developer.mozilla.org/en-US/search?q=%(query)s&topic=html",
        "coffee": "https://developer.mozilla.org/en-US/search?q=%(query)s",
        "php": "http://php.net/manual-lookup.php?pattern=%(query)s",
        "clojure": "http://clojuredocs.org/search?x=0&y=0&q=%(query)s",
        "go": "http://golang.org/search?q=%(query)s",
        "c": "http://www.cplusplus.com/search.do?q=%(query)s",
        "cpp": "http://www.cplusplus.com/search.do?q=%(query)s",
        "smarty": "http://www.smarty.net/%(query)s",
        "cmake": "http://cmake.org/cmake/help/v2.8.8/cmake.html#command:%(query)s",
        "perl": "http://perldoc.perl.org/search.html?q=%(query)s",
        "cs": "http://social.msdn.microsoft.com/Search/?query=%(query)s",
        "lua": "http://pgl.yoyo.org/luai/i/%(query)s",
        "pgsql": "http://www.postgresql.org/search/?u=%%2Fdocs%%2Fcurrent%%2F&q=%(query)s",
        "erlang": "http://erldocs.com/R16B03/?search=%(query)s",
        "haskell": "http://hayoo.fh-wedel.de/?query=%(query)s",
        "scala": "http://scalex.org/?q=%(query)s",
        "css": "http://devdocs.io/#q=%(scope)s+%(query)s",
        "scss": "http://devdocs.io/#q=%(scope)s+%(query)s",
        "less": "http://devdocs.io/#q=%(scope)s+%(query)s",
        "google": "https://google.com/search?q=%(scope)s+%(query)s",
        "python": {
            "command": ["python", "-m", "pydoc", "%(query)s"],
            "failTest": ".*no Python documentation found for.*",
            "changeMatch": "(Related help topics)",
            "changeWith": "-------\n\\1",
            "url": "http://docs.python.org/3/search.html?q=%(query)s"
        }
}

def combineDicts(dictionary1, dictionary2):
    new_dict = dictionary1.copy()
    new_dict.update(dictionary2)
    return new_dict

class GotoDocumentationCommand(sublime_plugin.TextCommand):
    """
    Search the selected text or the current word
    """
    def run(self, edit):
        # grab the word or the selection from the view
        for region in self.view.sel():
            location = False
            if region.empty():
                # if we have no selection grab the current word
                location = self.view.word(region)
            else:
                # grab the selection
                location = region

            if location and not location.empty():
                q = self.view.substr(location)
                scope = self.view.scope_name(location.begin()).rpartition('.')[2].strip()

                self.open_doc(q, scope)

    def open_doc(self, query, scope):

        settings = sublime.load_settings("goto_documentation.sublime-settings")

        # attach the prefix and suffix
        query = settings.get('prefix', '') + query + settings.get('suffix', '')

        # merge the default docs with the one provided by the user
        docs = combineDicts(default_docs, settings.get('docs'))

        # we use a temp scope so we don't replace the "real" scope
        tscope = scope

        if not tscope in docs:
            tscope = settings.get('fallback_scope', 'google')

        if not tscope in docs:
            self.show_status("No docs available for the current scope !")
            return



        # if we have the scope defined in settings
        # build the url and open it
        doc = docs[tscope]

        # if it is a dict we must have:
        #   - a command to run
        #   - a regex to check against
        #   - an optional fallback url
        if type(doc) is dict:
            # build the command
            command = [x%{'query': query, 'scope': scope} for x in doc['command']]

            # Per http://bugs.python.org/issue8557 shell=True
            shell = os.name == 'nt'
            # run it
            process = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = [x.decode('unicode_escape').rstrip() for x in process.stdout.readlines()]

            stdout = '\n'.join(stdout)


            # match the result agains the regex
            reg = re.compile(doc['failTest'])
            if reg.match(stdout):
                # use the fallback url
                if 'url' in doc:
                    fullUrl = doc['url']%{'query': query, 'scope': scope}
                    webbrowser.open(fullUrl)
                else:
                    self.show_status("No docs available for the current word !")


            else:
                # regex to change something before it's sent to the panel
                if 'changeMatch' in doc and 'changeWith' in doc:
                    stdout = re.sub(doc['changeMatch'], doc['changeWith'], stdout)

                # we have a valid result from console
                # so we place it in the output panel
                self.panel(stdout)

        else:
            if not doc:
                self.show_status("This scope is disabled !")
                return

            # we have an url so we build and open it
            fullUrl = doc%{'query': query, 'scope': scope}
            webbrowser.open(fullUrl)


    # Open and write on the output panel
    def panel(self, output):
        active_window = sublime.active_window()

        if not hasattr(self, 'output_view'):
            self.output_view = active_window.get_output_panel("gotodocumentation")

        self.output_view.set_read_only(False)

        self.output_view.run_command('goto_documentation_output', {
            'output': output,
            'clear': True
        })

        self.output_view.set_read_only(True)
        active_window.run_command("show_panel", {"panel": "output.gotodocumentation"})

    def show_status(self, status):
        sublime.status_message(status)
        print("\nGoto Documentation Plugin: " + status + "\n")




class GotoDocumentationOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output = '', output_file = None, clear = False):

        if clear:
            region = sublime.Region(0, self.view.size())
            self.view.erase(edit, region)

        self.view.insert(edit, 0, output)


