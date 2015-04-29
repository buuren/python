
https://julien.danjou.info/blog/2013/guide-python-static-class-abstract-methods

Python OOP:

1) Classes

old construct:

class ClassName:
    """
    An old style class that
    isn't using inheritance.
    """
    
new (python 2.7):

class ClassName(object):

After creaing the class, make __init__ method

def __init__(self, some_value):
  self.some_property = some_value

def print_name(self):
  print some_variable


2) def on_the_menu(arg, *args, **kwargs):
 
arg = variable
*args = tuple
**kwargs = dictionary
 
 
3)if name == __init__
 
 
file1.py:
import file2.py
 
file2.py:
if __name__ == '__main__'
  print 'hi main!'
  
run file1.py - nothing happens
run file2.py - 'hi main!' because file2 is main
