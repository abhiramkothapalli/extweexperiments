from distutils.core import setup, Extension

"""
setup.py file for SWIG example
"""

extra_compile_args = ["-DCPP"]

gfeccore_module = Extension('_gfeccore',
                            include_dirs = ['../include'],
                            libraries = ['zm'],
                            library_dirs = ['../lib'],
                            sources = ['gfeccore.cpp', 'gfeccore.i'],
                            extra_compile_args = extra_compile_args,
                            swig_opts=['-c++'])


setup (name = 'GFECcore',
       version = '1.0',
       description = 'Core GFEC functionality',
       ext_modules = [gfeccore_module],
       py_modules = ["gfeccore"])


#swig -python -c++ gfeccore.i
