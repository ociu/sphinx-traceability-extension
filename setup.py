# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

project_url = 'https://github.com/melexis/sphinx-traceability-extension'

requires = ['Sphinx>=0.6', 'docutils', 'natsort', 'matplotlib']

setup(
    name='mlx.traceability',
    use_scm_version={
        'write_to': 'mlx/__traceability_version__.py'
    },
    setup_requires=['setuptools_scm'],
    url=project_url,
    license='GNU General Public License v3 (GPLv3)',
    author='Stein Heselmans',
    author_email='teh@melexis.com',
    description='Sphinx traceability extension (Melexis fork)',
    long_description=open("README.rst").read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(exclude=['tests', 'doc']),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['mlx'],
    keywords=[
        'traceability',
        'requirements engineering',
        'requirements management',
        'software engineering',
        'systems engineering',
        'sphinx',
        'requirements',
        'ASPICE',
        'ISO26262',
        'ASIL',
    ],
    package_data={'mlx.traceability': ['assets/*.js']},
)
