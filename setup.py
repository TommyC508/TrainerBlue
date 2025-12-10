from setuptools import setup, find_packages

setup(
    name="pokemon-showdown-agent",
    version="0.1.0",
    description="AI agent for playing Pokemon Showdown",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "websockets>=10.0",
        "aiohttp>=3.8.0",
        "numpy>=1.21.0",
        "torch>=1.12.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
        "tenacity>=8.0.0",
        "tqdm>=4.64.0",
    ],
    python_requires=">=3.9",
)
