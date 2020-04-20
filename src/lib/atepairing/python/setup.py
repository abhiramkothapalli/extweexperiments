from distutils.core import setup, Extension

module1 = Extension('wrapper',
                    include_dirs = ['../include'],
                    libraries = ['zm'],
                    library_dirs = ['../lib'],
                    sources = ['wrapper.cpp'])

setup (name = 'Wrapper',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
