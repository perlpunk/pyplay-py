"""\
Python Interactive Playground
"""

__version__ = '1.0.5'

import os
import sys

class PyPlay():
    def __init__(self):
        self.config = self.Config()

        modules = self.config.modules
        for option in os.environ['_PYPLAY_ARGV'].split():
            if option == '--none':
                modules = []
            elif option.startswith('-'):
                module = option[1:]
                try:
                    modules.remove(module)
                except ValueError:
                    pass
            else:
                module = option
                modules.append(module)

        for module in reversed(modules):
            command = "import %s" % module
            self.config.commands.insert(0, command)

    def set_pythonpath(self):
        if self.config.ENV_CONFIG_DIR != '':
            for dir in (
                self.config.HOME_CONFIG_DIR,
                self.config.LOCAL_CONFIG_DIR,
                self.config.ENV_CONFIG_DIR,
            ):
                if dir is not None:
                    sys.path.insert(0, dir)

        for path in reversed(self.config.pythonpath):
            sys.path.insert(0, path)

    def init_readline(self):
        try:
            import readline
        except ImportError:
            print("Module readline not available.")
        else:
            import rlcompleter
            readline.parse_and_bind("tab: complete")

    def help(self, vars):
        locals().update(vars)
        dir = self.config.ENV_CONFIG_DIR
        if dir is None:
            dir = 'None'
        config = (
            self.config.CONFIG_FILE or
            'None found. See PyPlay documentation.'
        )
        return """
Welcome to PyPlay version %(version)s.

PYPLAY_CONFIG_DIR:  %(dir)s
Config file:        %(config)s
Commands:
    * h()           -- Help screen.
    * y(...)        -- Print a YAML dump of any object.
                       For example, try: y(__builtins__.__dict__)

Tips and Tricks:
    * Use the tab key to complete a word or see what options are
      available in any given context.
    * Use <ctl>-L to clear the screen.

Full documentation: http://pypi.python.org/pypi/pyplay/
""" % locals()

    def main(self):
        version = __version__
        l = locals()

        def h():
            print(pyplay.help(l))

        def config():
            y(pyplay.config)

        def y(object):
            import yaml
            yaml_dump = yaml.dump(
                object,
                default_flow_style=False,
                explicit_start=True
            )
            output = False
            if pyplay.config.highlight_yaml:
                try:
                    import pipes
                    t = pipes.Template()
                    t.append(pyplay.config.highlight_yaml, '--')
                    # TODO
                    f = t.open('/tmp/pipefile-pyplay', 'w')
                    f.write(yaml_dump)
                    f.close()
                    highlighted = open('/tmp/pipefile-pyplay').read()
                    print(highlighted)
                    output = True
                except err:
                    print(format(err))

            if not output:
                print(yaml_dump)

        globals().update({'h': h, 'y': y, 'config': config})

        pyplay = PyPlay()

        pyplay.set_pythonpath()

        print('*** Welcome to PyPlay version %s -- Type h() for help.' % (
            __version__,))

        if pyplay.config.CONFIG_FILE:
            print("*** PyPlay config file: '%s'" % pyplay.config.CONFIG_FILE)

        if pyplay.config.readline:
            print('*** PyPlay tab completion enabled')
            pyplay.init_readline()

        del globals()['os']
        del globals()['sys']
        del globals()['__version__']
        del globals()['PyPlay']

        for command in pyplay.config.commands:
            print('>>> %s' % command)
            exec(command, globals())

    class Config():
        dir = os.path.expanduser('~/.pyplay')
        HOME_CONFIG_DIR = dir if os.path.exists(dir) else None

        dir = './pyplay'
        LOCAL_CONFIG_DIR = dir if os.path.exists(dir) else None

        dir = os.environ.get('PYPLAY_CONFIG_DIR', None)
        ENV_CONFIG_DIR = dir if (not dir or os.path.exists(dir)) else None

        dir = ENV_CONFIG_DIR or LOCAL_CONFIG_DIR or HOME_CONFIG_DIR
        file = dir + '/config.yaml' if dir else None
        if ENV_CONFIG_DIR == '':
            CONFIG_FILE = None
        else:
            CONFIG_FILE = file if (dir and os.path.exists(file)) else None

        def __init__(self):
            self.readline = True
            self.commands = []
            self.pythonpath = [
                'lib',
            ]
            self.modules = [
                'os',
                'sys',
                're',
            ]
            self.highlight_yaml = None

            if self.CONFIG_FILE:
                import yaml
                config = yaml.load(open(self.CONFIG_FILE, 'r'))
                self.__dict__.update(config)


if __name__ == '__main__':
    PyPlay().main()
