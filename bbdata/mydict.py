import json


class mydict(dict):
    def __getattr__(self, key):
        return self.get(key, '')

    def __setattr__(self, key, value):
        self[key] = value

    def __add__(self, data):
        return mydict(self.items() + data.items())

    def __sub__(self, key):
        return mydict((k, v) for (k, v) in self.items() if k != key)


def jout(d):
    opts = {"ensure_ascii": False, "sort_keys": True}
    return json.dumps(d, indent=4, separators=(',', ': '), **opts)
