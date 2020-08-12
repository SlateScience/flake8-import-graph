from pkg import normal  # disallowed - in parent package
from pkg.pkg2 import sibling  # allowed - in package


__all__ = ['normal', 'sibling']
