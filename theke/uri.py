import re
from urllib.parse import unquote, quote

class ThekeURI:
    def __init__(self, URI, isRaw = False):
        self.URIprefix, self.path, self.params = self.parse_URI(URI)

        if self.URIprefix != 'theke:///':
            raise ValueError("Unsupported ThekeURI ({})".format(self.URIprefix))

    def parse_URI(self, URI):
        """Parse the URI.
        @return: prefix, path, parameters
        """
        reURI = re.compile(r"^(\w+:\/\/\/)([^\?]+)(\?(.+))?$")
        m = reURI.match(URI)

        if m:
            if m.group(3) is not None:
                # Parse parameters in a dict (m.group(4))
                params = {}
                for p in m.group(4).split('&'):
                    name, value = p.split('=')
                    params[name] = value
                return m.group(1), m.group(2), params

            else:
                return m.group(1), m.group(2), {}
        else:
            raise ValueError("Invalid ThekeURI")

    def get_decoded_URI(self):
        if len(self.params) > 0:
            return self.URIprefix + self.path + '?' + '&'.join([name + '=' + value for name, value in self.params.items()])
        else:
            return self.URIprefix + self.path

    def get_coded_URI(self):
        if len(self.params) > 0:
            return self.URIprefix + quote(self.path) + '?' + '&'.join([name + '=' + quote(value) for name, value in self.params.items()])
        else:
            return self.URIprefix + quote(self.path)

    def __repr__(self):
        return self.get_decoded_URI()


if __name__ == "__main__":
    uri1 = ThekeURI("theke:///bible/John 1:1?source=MorphGNT")
    print(uri1.get_decoded_URI())
    print(uri1.get_coded_URI())

    uri2 = ThekeURI("theke:///welcome.html")
    print(uri2.get_decoded_URI())
    print(uri2.get_coded_URI())