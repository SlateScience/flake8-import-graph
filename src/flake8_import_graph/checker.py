import ast
import os.path
from . import __version__


def is_prefix(a, b):
    return a == b[:len(a)]


class ImportVisitor(ast.NodeVisitor):

    def __init__(self, current_module, dest, denied, relative_imports_allowed):
        self.dest = dest
        self.current_module = current_module
        mod_path = current_module.split('.')
        self.mod_path = mod_path
        self.denied = [v for k, v in denied if is_prefix(k, mod_path)]
        self.in_package_allowed = [
            k for k, v in denied if is_prefix(k, mod_path)
        ]
        self.relative_allowed = any(
            is_prefix(k, mod_path) for k in relative_imports_allowed
        )

    def visit_Import(self, node):  # noqa: N802
        for name in node.names:
            if self.not_allowed(name.name):
                self.dest.append((
                    node.lineno, node.col_offset,
                    'IMP001 Denied import {}'.format(name.name),
                    'ImportGraphChecker'))

    def visit_ImportFrom(self, node):  # noqa: N802
        if node.level > 0:
            if self.relative_allowed:
                return
            mod_path = self.mod_path[:-node.level]
            if node.module:
                mod_path.append(node.module)
            mod_name = '.'.join(mod_path)
        else:
            mod_name = node.module
        if self.not_allowed(mod_name):
            self.dest.append((
                node.lineno, node.col_offset,
                'IMP001 Denied import {}'.format(mod_name),
                'ImportGraphChecker'))
        for name in node.names:
            full = mod_name + '.' + name.name
            if self.not_allowed(full):
                self.dest.append((
                    node.lineno, node.col_offset,
                    'IMP001 Denied import {}'.format(full),
                    'ImportGraphChecker'))


    def not_allowed(self, name):
        dotted = name.split('.')
        return (
            any(is_prefix(item, dotted) for item in self.denied)
            and
            not any(is_prefix(item, dotted) for item in self.in_package_allowed)
        )


class ImportGraphChecker:
    name = "import-graph"
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        path = os.path.splitext(filename)[0]
        mod_path = []
        while path:
            if os.path.exists(os.path.join(path, '.flake8')):
                break
            dir, name = os.path.split(path)
            mod_path.insert(0, name)
            path = dir
        self.module = '.'.join(mod_path)

    @classmethod
    def parse_options(cls, options):
        cls.denied_imports = []
        for item in options.deny_imports:
            src, dest = item.split('=', 1)
            cls.denied_imports.append((src.split('.'), dest.split('.')))
        cls.exemptions = [src.split('.') for src in options.allow_all_imports]
        cls.relative_imports_allowed = [
            pkg.split('.') for pkg in options.allow_relative_imports
        ]

    def run(self):
        errors = []
        if not any(is_prefix(exemption, self.module.split('.'))
                   for exemption in self.exemptions):
            visitor = ImportVisitor(
                self.module, errors,
                self.denied_imports, self.relative_imports_allowed
            )
            visitor.visit(self.tree)
        yield from errors

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            '--deny-imports', type='str', comma_separated_list=True,
            default=[], parse_from_config=True,
            help='A list of denied imports like '
                 '`mypkg.where=other_pkg.disallowed_sub_package`.',
        )
        parser.add_option(
            '--allow-relative-imports', type='str', comma_separated_list=True,
            default=[], parse_from_config=True,
            help='A list of packages where relative imports are allowed, like '
                 '`mypkg.where.clean_module`.',
        )
        parser.add_option(
            '--allow-all-imports', type='str', comma_separated_list=True,
            default=[], parse_from_config=True,
            help='A list of modules exempted from import denials like '
                 '`mypkg.where.exempted_module`.'
        )
