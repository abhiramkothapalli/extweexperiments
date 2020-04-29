from distutils.core import setup, Extension

"""
setup.py file for SWIG example
"""

gfeccore_module = Extension('gfeccore',
                            include_dirs = ['../include'],
                            library_dirs = ['../lib'],
                            sources = ['gfeccore.cpp', 'gfeccore.i'],
                            extra_compile_args = ["-DCPP -x c++"],)

setup (name = 'GFECcore',
       version = '1.0',
       description = 'Core GFEC functionality',
       ext_modules = [gfeccore_module],
       py_modules = ["gfeccore"])
