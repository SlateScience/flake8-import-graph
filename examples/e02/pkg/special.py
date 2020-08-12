import file1  # allowed -- all allowed in this file
from pkg.pkg2 import inpkg  # allowed -- all allowed in this file

__all__ = ['file1', 'inpkg']
