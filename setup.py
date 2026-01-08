from setuptools import setup, find_packages

# requirements.txt 파일 읽기
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="kbo_dashboard",
    version="0.1",
    packages=find_packages(),
    install_requires=required
)