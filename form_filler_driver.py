
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 20:16:53 2021

@author: heslinr1
"""
from itertools import chain, islice, repeat
from form_filler import *
import argparse as ap
import sys
import shelve

# Based on https://stackoverflow.com/questions/38666283/is-it-possible-to-assign-a-default-value-when-unpacking
def pad_with_none(string, length = 2, sep = "=", fill = None):
    lst = islice(chain(string.split(sep), repeat(fill)), length)
    return list(map(lambda x: x.strip() if x else x, lst))
                 

class InstanceAction(ap.Action):
    def __call__(self, parser, namespace, argument_values, option_string = None):
        if argument_values in globals():
            print(f"Error: name {argument_values} already in use")
            sys.exit(1)
        setattr(namespace, "instance", argument_values)
    
class MappingsAction(ap.Action):
    def __call__(self, parser, namespace, argument_values, option_string = None):
        
        args_split = list(map(pad_with_none, argument_values))
        
        if args_split and (longest := max(map(len, args_split))) >2:
             print(f"Error: mapping arg split into {longest} pieces. Need at most 2.")
             sys.exit(1)
            
        args_dict = dict(args_split)
        setattr(namespace, "mappings", args_dict)
        
parser = ap.ArgumentParser(description = """Argument parser for creating instances
                           of FormFiller """)
parser.add_argument("-s", "--submit", default = None, nargs = None, 
                    help = """CSS selector for website
                    submit button. If omitted (recommended), FormFiller instead
                    sends an ENTER keypress to the last input reached.""")
parser.add_argument("instance",    help = """Name for instance of
                    FormFiller to create""")
parser.add_argument("url", help = """URL of website to create FormFiller
                    object for""")
parser.add_argument("storage", help = """Path to shelve file in which to store
                    the created object. Will be created if it does not already
                    exist.""")
parser.add_argument("mappings", nargs = "*", action = MappingsAction,
                    help = """Zero or more key-value pairs of the form
                    <selector>=<input text>. Arguments without an = are
                    keyed to None.""")

parsed = parser.parse_args()
args = vars(parsed)


#Only quote submit if not None
quote_submit = "'" if args["submit"] else ""
code = f"{args['instance']} = FormFiller('{args['url']}', {quote_submit}{args['submit']}{quote_submit}, {args['mappings']})"
code = compile(code, "string", "exec")
exec(code)

name = compile(args["instance"], "string", "eval")

storage = shelve.open(args["storage"])
storage[args["instance"]] = eval(name)
storage.close()