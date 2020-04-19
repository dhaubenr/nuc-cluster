#!/usr/bin/python

class FilterModule(object):
    '''
    Custom Ansible filter plugin that converts a given
    ASCII character to it's corresponding ordinal value
    or vice versa, basically making Python's ord() and chr()
    functions available to the Jinja2 templating engine.
    For ASCII characters 'a' to 'z' the contiguous range
    of ordinals is 97 to 122.
    '''

    def filters(self):
        return {
            'chr': self.ordinal_to_char,
            'ord': self.char_to_ordinal
        }

    def ordinal_to_char(self, ordinal):
        return str(chr(ordinal))

    def char_to_ordinal(self, char):
        return ord(char)
