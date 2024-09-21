from setuptools import setup, find_packages

setup(
    name="local_model_api",
    version="0.1",
    description="A Local Language Model Server-Client API for Efficient Resource Sharing and Adaptive Model Loading.",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "transformers",
        "pyyaml",
        "requests",
        "gunicorn",
        "peft"
    ],
)
