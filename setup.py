import os
import sys
import platform
from setuptools import setup, Extension
from pathlib import Path

SNAPPY_DIR = Path(__file__).parent / "snappy"

snappy_sources = [
    "snappy/snappy.cc",
    "snappy/snappy-sinksource.cc",
    "snappy/snappy-c.cc",
]

if not SNAPPY_DIR.exists():
    print("Error: snappy source directory not found!")
    sys.exit(1)

extra_compile_args = []
extra_link_args = []
define_macros = [
    ('HAVE_STDINT_H', '1'),
    ('HAVE_STDDEF_H', '1'),
    ('HAVE_SYS_UIO_H', '1'),
]

if platform.system() == "Windows":
    extra_compile_args = ['/O2', '/W3', '/std:c++14']
    define_macros.append(('_CRT_SECURE_NO_WARNINGS', '1'))
    # Windows不支持sys/uio.h
    define_macros = [m for m in define_macros if m[0] != 'HAVE_SYS_UIO_H']
elif platform.system() == "Darwin":  # macOS
    extra_compile_args = ['-O3', '-std=c++14', '-mmacosx-version-min=10.9']
    extra_link_args = ['-mmacosx-version-min=10.9']
elif platform.system() == "Linux":
    extra_compile_args = ['-O3', '-std=c++14']

snappy_ext = Extension(
    'snappy_py',
    sources=['src/snappy_module.c'] + snappy_sources,
    include_dirs=[
        str(SNAPPY_DIR),
        str(SNAPPY_DIR.parent),
    ],
    define_macros=define_macros,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++',
    py_limited_api=False,  # 提高性能
)

setup(
    ext_modules=[snappy_ext],
)