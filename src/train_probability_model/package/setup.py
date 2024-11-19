from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
    'torch>=2.0.0',
    'numpy>=1.19.2',
    'pandas>=1.1.3',
    'scikit-learn>=0.23.2',
    'wandb>=0.12.0',
    'google-cloud-storage>=2.0.0'
]

setup(
    name='trainer',
    version='0.0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='Tennis Match Prediction Training Application',
    python_requires='>=3.7',
)