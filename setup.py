from setuptools import setup

requires = []

setup(
    name='app',
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = app:main
    """,
)
