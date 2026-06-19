from setuptools import setup, Extension
import sys
import os

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __str__(self):
        import pybind11
        return pybind11.get_include()

ext_modules = [
    Extension(
        'bio_core_cpp',
        ['src/cpp/bio_core.cpp', 'src/cpp/serial_reader.cpp', 'src/cpp/audio_feedback.cpp', 'src/cpp/signal_analyst.cpp'],
        include_dirs=[
            get_pybind_include(),
            'src/cpp'
        ],
        language='c++',
        extra_compile_args=['/std:c++17'] if sys.platform == 'win32' else ['-std=c++17']
    ),
]

setup(
    name='bio_core_cpp',
    version='0.1.0',
    description='C++ Core Modules for Bio-Telemetry Interface',
    ext_modules=ext_modules,
    setup_requires=['pybind11>=2.5.0'],
    install_requires=['pybind11>=2.5.0'],
)
