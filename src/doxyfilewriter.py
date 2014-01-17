
def _quote(txt):
    return '"' + txt + '"'

class DoxyfileWriter(object):
    """Makes it easy to write entries in a Doxyfile, correctly handling quoting
    """
    def __init__(self, fl):
        self.fl = fl

    def write_entry(self, key, value):
        """Write an entry

        key -- the key part of the entry
        value -- the value part of the entry. Can be a string, a list, a tuple or a boolean"""
        if isinstance(value, (list, tuple)):
            txt = ' '.join([_quote(x) for x in value])
        elif isinstance(value, bool):
            txt = ['NO', 'YES'][value]
        else:
            txt = _quote(str(value))
        self.fl.write(key + ' = ' + txt + '\n')

    def write_entries(self, **kwargs):
        """ Call write_entry for all arguments passed"""
        for key, value in kwargs.items():
            self.write_entry(key, value)
