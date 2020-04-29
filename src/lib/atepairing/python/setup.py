from distutils.core import setup, Extension

"""
setup.py file for SWIG example
"""

extra_compile_args = ["-DCPP"]

gfeccore_module = Extension('gfeccore',
                            include_dirs = ['../include'],
                            library_dirs = ['../lib'],
                            sources = ['gfeccore.i'],
                            extra_compile_args = extra_compile_args,)

setup (name = 'GFECcore',
       version = '1.0',
       description = 'Core GFEC functionality',
       ext_modules = [gfeccore_module],
       py_modules = ["gfeccore"])
