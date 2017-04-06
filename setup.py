from setuptools import setup

setup(
    name='picobuild',
    version='0.1.0',
    license='MIT',
    py_modules=["picobuild"],
    install_requires=['click'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'picobuild=picobuild:main',
        ],
    }
)
