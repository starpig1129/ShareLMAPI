from setuptools import setup, find_packages

setup(
    name="ShareLMAPI",  # 套件的名稱
    version="0.1.0",  # 套件的版本
    author="Your Name",
    author_email="james911129@gmail.com",
    description="A local language model API for sharing models between programs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/starpig1129/ShareLMAPI",
    packages=find_packages(),  # 自動查找所有 Python 包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        "fastapi",
        "uvicorn",
        "transformers",
        "pytest",
        "requests",
        "peft",
        "bitsandbytes", 
        "pydantic"
    ],
)
