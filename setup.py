from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='dm-logger',
    version='0.6.7',
    author='dimka4621',
    author_email='mismartconfig@gmail.com',
    description='This is my custom logger',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/dm-logger',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='dm-logger',
    project_urls={
        'GitHub': 'https://github.com/MykhLibs/dm-logger'
    },
    python_requires='>=3.8'
)
