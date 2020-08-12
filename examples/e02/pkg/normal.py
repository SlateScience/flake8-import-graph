import file1  # disallowed, specific
from pkg import special  # disallowed, specific
from pkg.pkg2 import inpkg  # allowed

__all__ = ['file1', 'special', 'inpkg']
