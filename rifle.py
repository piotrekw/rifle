#!/usr/bin/env python
import collections
import os
import pip
import pkg_resources
import sys


DEFAULT_RFILE = os.environ.get('DEFAULT_RFILE', 'requirements.txt')


def get_pkg_version(name):
    name = name.lower()
    for pkg in pip.get_installed_distributions():
        if pkg.key.lower() == name:
            return pkg.version
    raise KeyError('Package does not exist')


class RFile(object):
    def __init__(self, path=DEFAULT_RFILE):
        self.path = path
        self.read()

    def read(self):
        self.reqs = []
        requirements = open(self.path, 'r').read()
        for requirement in pkg_resources.parse_requirements(requirements):
            self.reqs.append(requirement)

    def write(self):
        self.reqs.sort(key=lambda req: req.key)
        requirements = '\n'.join(str(req) for req in self.reqs)
        with open(self.path, 'w') as rfile:
            rfile.write(requirements)

    def add(self, pkg):
        req = pkg_resources.Requirement.parse(pkg)
        for r in self.reqs:
            if r.key == req.key:
                print 'Package already installed: %s' % req.key
                sys.exit(1)
        reload(pkg_resources)
        req.specs.append(('==', get_pkg_version(pkg)))
        self.reqs.append(req)


def init(rfile=DEFAULT_RFILE):
    if os.path.exists(rfile):
        print 'File already exists: %s' % rfile
        sys.exit(1)
    open(rfile, 'w').close()


def add(pkg, rfile=DEFAULT_RFILE):
    pip.main(['install', pkg, '-q'])
    rfile = RFile(rfile)
    rfile.add(pkg)
    rfile.write()


commands = [init, add]


def main():
    if len(sys.argv) < 2:
        print 'usage: rifle.py <command> [...]'
        sys.exit(-1)
    command = sys.argv[1]
    args = sys.argv[2:]
    for cmd_func in commands:
        if cmd_func.__name__ == command:
            cmd_func(*args)
            break
    else:
        print 'Unknown command'
        sys.exit(2)


if __name__ == '__main__':
    main()
