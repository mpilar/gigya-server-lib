from distutils.core import setup
import gslib

setup(
    name='gigyasocial',
    version=gslib.__version__,
    author=gslib.__author__,
    author_email='miguel@miguelpilar.com',
    packages=['gslib'],
    url='http://pypi.python.org/pypi/GigyaLib/',
    license=open('LICENSE.txt').read(),
    description='The Gigya Social Library (gslib) is a python adaptation of the Gigya Social Server SDK',
    long_description=open('README.rst').read(),
    install_requires=[
        "requests>=0.13.6"
    ],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
    ),
)
