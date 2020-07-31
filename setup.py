import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.txt")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()

requires = [
    "deform",
    "plaster_pastedeploy",
    "pyramid",
    "pyramid_deform",
    "pyramid_jinja2",
    "pyramid_debugtoolbar",
    "traktor_nml_utils@git+https://github.com/jlantz/traktor-nml-utils#egg=traktor_nml_utils",
    "waitress",
]

tests_require = [
    "WebTest >= 1.3.1",  # py3 compat
    "pytest >= 3.7.4",
    "pytest-cov",
]

setup(
    name="epeus_nml_tools",
    version="0.0",
    description="Web app for tools that do neat things with Traktor NML files",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="",
    author_email="",
    url="",
    keywords="web pyramid pylons",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={"testing": tests_require,},
    install_requires=requires,
    entry_points={"paste.app_factory": ["main = epeus_nml_tools:main",],},
)
