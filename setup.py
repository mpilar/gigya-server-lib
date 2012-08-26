from distutils.core import setup

setup(
    name='gigya-server-lib',
    version="0.1.3",
    author="Miguel Pilar",
    author_email='miguel@miguelpilar.com',
    packages=['gslib'],
    url='http://pypi.python.org/pypi/GigyaServerLib/',
    license=open('LICENSE.txt').read(),
    description='Gigya Server Library (gslib) is a python adaptation of the Gigya Server SDK',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    install_requires=[
        "requests"
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
