import setuptools
from psd_to_usd.version import Version

setuptools.setup(name='psd_to_usd',
                 version=Version('0.1.0').number,
                 description="Convert PSD files to Pixar's Universal Scene Description",
                 long_description=open('README.md').read().strip(),
                 author='Ben Skinner',
                 author_email='ben.vochsel@gmail.com',
                 url='https://github.com/Vochsel/psd_to_usd',
                 py_modules=['psd_to_usd'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='usd, psd',
                 classifiers=['PSD', 'USD'])
