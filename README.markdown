GotoDocumentation
===========================
A Sublime Text plugin to jump to documentation for the current keyword.


## Supports

 * PHP
 * JS / CoffeeScript
 * HTML
 * CSS/SASS/LESS
 * Python (via `pydoc`)
 * Clojure
 * Go
 * Ruby (+Rails)
 * C / C++
 * Perl
 * C#
 * Lua
 * Postgres
 * Erlang
 * Smarty
 * Haskell
 * ...you can add any other language via settings


Installation
--------------

**Via Package Control**  
Search for `GotoDocumentation`

**Manually**  
Clone this project in your Packages folder under the name `GotoDocumentation`.  
`git clone https://github.com/kemayo/sublime-text-2-goto-documentation.git GotoDocumentation`


How to use
----------------
Move the cursor inside the word you want the docs for and: 
 * Press `Super+Shift+H` or  
 * Open command palette (Ctrl+Shift+P) and search for for GotoDocumentation

## Edit the urls
GotoDocumentation allows you to edit the url that opens by editing the settings.
### The available settings are:
```json
{
    "prefix": "", // added at the begging of the query
    "suffix": "", // added at the end of the query
    "docs": { // obj containing the docs for each scope
              // these are merged with the default ones


        // the key value pair represent scope -> doc url
        // supported placeholders:
        //  - %(query)s the selected text/word
        //  - %(scope)s the current scope
       "css": "http://devdocs.io/#q=%(scope)s+%(query)s",

        // we can also have an object to
        // run a command for finding docs
        // inside the command you can use the same placeholders
        "python": {
            // the command to be executed
            "command": ["python", "-m", "pydoc", "%(query)s"],
            // a regex to determine if this was an invalid response from the console
            "failTest": ".*no Python documentation found for.*",
            // regex to select something from the valid response
            "changeMatch": "(Related help topics)",
            // regex to replace the matched result
            "changeWith": "-------\n\\1",
            // fallback url: if failTest returns true this will be used
            "url": "http://docs.python.org/3/search.html?q=%(query)s"
        }
    },
    // if we have no docs for the current scope
    // we will try using the fallback one,
    // to disable set to false
    "fallback_scope": "google"
}

```
The change replace is done with the [`re.sub`](https://docs.python.org/2/library/re.html#re.sub) method 

## How to get the scope
To get the scope for a specific place open your sublime console with `` ctrl + ` `` and paste in this command
`view.scope_name(view.sel()[0].begin()).rpartition('.')[2].strip()`  
You can then use that scope to set a rule in the `docs` dictionary(object).


Contributions
-----------------
Submit a patch adding more and I'll include it.  

If you find a bug or have suggestions open an issue [here](https://github.com/kemayo/sublime-text-2-goto-documentation/issues)




