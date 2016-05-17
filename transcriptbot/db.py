import os
import getpass
import json
import errno

from tabulate import tabulate


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class DB(object):
    def __init__(self, path):
        self.path = path
        retrieved = self.retrieve()
        if retrieved:
            self.hooks = map(Hook.deserialize, retrieved['hooks'])
            if retrieved['active_hook']:
                self.active_hook = Hook.deserialize(retrieved['active_hook'])
            else:
                self.active_hook = None
            self.name = retrieved['name']
        else:
            self.hooks = []
            self.active_hook = None
            self.name = getpass.getuser()

    @classmethod
    def load(self, path=os.path.expanduser("~/.micbot/")):
        return DB(path)

    def print_hooks(self):
        data = []
        for h in self.hooks:
            name = h.name
            if self.active_hook == h:
                name += " (ACTIVE)"
            data.append([name, h.url])
        print tabulate(data, headers=["Name", "URL"], tablefmt="grid")

    def retrieve(self):
        if os.path.exists(self.path_to_db()):
            return json.load(open(self.path_to_db()))

    def path_to_db(self):
        return os.path.join(self.path, "db.json")

    @property
    def hook_names(self):
        return map(lambda h: h.name, self.hooks)

    def get_hook(self, name):
        for hook in self.hooks:
            if hook.name == name:
                return hook

    def add_hook(self, name, url):
        if name in self.hook_names:
            return False
        hook = Hook(name, url)
        self.hooks.append(hook)
        if len(self.hooks) == 1:
            self.set_active_hook(hook)
        self.save()
        return True

    def save(self):
        mkdir_p(self.path)
        json.dump(self.serialize(), open(self.path_to_db(), "w"))

    def remove_hook(self, name):
        hook = self.get_hook(name)
        if hook:
            self.hooks.remove(hook)
            self.save()
            return True
        else:
            return False

    def set_active_hook(self, hook):
        self.active_hook = hook
        self.save()

    def serialize(self):
        hooks = map(lambda h: h.serialize(), self.hooks)
        if self.active_hook:
            active_hook = self.active_hook.serialize()
        else:
            active_hook = None
        return {
            'hooks': hooks,
            'active_hook': active_hook,
            'name': self.name
        }


class Hook(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def print_(self):
        print '%s - %s' % (self.name, self.url)

    @classmethod
    def deserialize(self, obj):
        return Hook(obj['name'], obj['url'])

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def serialize(self):
        return {
            'name': self.name,
            'url': self.url
        }
