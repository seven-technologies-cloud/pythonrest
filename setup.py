from setuptools import setup

setup(
    name='pythonrest',
    version='0.1.0',
    description='Third Pypi test release for this Seven Technologies Clouds API, the PythonRestCLI',
    py_modules=['pythonrest'],
    install_requires=['Click'],
    entry_points={
        'console_scripts': [
            'pythonrest=app:cli',
        ],
    },
)
