import os
from setuptools import setup, Command

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS=('irs',),
            USE_TZ=True,
            SECRET_KEY='test-secret-key-for-testing-only',
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )
        from django.core.management import call_command
        import django
        django.setup()
        settings.BASE_DIR = os.path.dirname(__file__)
        call_command('test', 'irs')

setup(
    name='django-irs-filings',
    version='0.2.0',
    packages=['irs'],
    include_package_data=True,
    license='MIT',
    description='A Django app to download IRS 527 filings and load them into a database',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/sahilchinoy/django-irs',
    author='Sahil Chinoy',
    author_email='sahil.chinoy@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 5.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
    install_requires=[
        'Django>=5.1,<5.2',
        'requests>=2.32.0',
    ],
    cmdclass={
        'test': TestCommand
    },
)
