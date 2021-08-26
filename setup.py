import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sponsorblock.py",
    version="0.1.0",
    author="Wasi Master",
    author_email="arianmollik323@gmail.com",
    description="An unofficial wrapper for the SponsorBlock API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://wasi-master.github.io/sponsorblock/",
    project_urls={
        "Github": "https://github.com/wasi-master/sponsorblock",
        "Bug Tracker": "https://github.com/wasi-master/sponsorblock/issues",
        "Documentation": "https://sponsorblock.readthedocs.io",
        "Say Thanks": "https://saythanks.io/to/arianmollik323@gmail.com",
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Internet"

    ],
    packages=["sponsorblock"],
    python_requires=">=3.6",
    install_requires=["requests"],
)
