# Sublime Text 2 plugin: Goto Documentation

A command to jump to documentation for the current word.

# Supports

 * PHP
 * JS

Submit a patch adding more and I'll include it.

# Using

Open the command palette (cmd-shift-p) and choose "Goto Documentation" while your cursor is on a word.

Make a keybind by adding the following to your `User/Default (OSX).sublime-keymap`:

	{ "keys": ["super+shift+h"], "command": "goto_documentation" }

(I don't like plugins automatically adding keybinds, okay.)
