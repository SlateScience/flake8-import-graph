import file1  # allowed -- no rule targets this file
from pkg import normal, special  # allowed -- no rule targets this file


__all__ = ['file1', 'normal', 'special']
