<!-- markdownlint-disable-file MD033-->

<!-- PROJECT LOGO -->
<br/>
<p align="center">
  <a href="https://github.com/wasi-master/sponsorblock.py">
    <img src="https://raw.githubusercontent.com/wasi-master/sponsorblock.py/main/images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h2 align="center">sponsorblock.py</h2>

  <p align="center">
    A wrapper for the SponsorBlock API
    <br />
    <a href="https://sponsorblockpy.readthedocs.io/en/latest/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/wasi-master/sponsorblock.py/blob/main/demo.md">View Demo</a>
    ·
    <a href="https://github.com/wasi-master/sponsorblock.py/issues">Report Bug</a>
    ·
    <a href="https://github.com/wasi-master/sponsorblock.py/issues">Request Feature</a>
  </p>
</p>

<p align="center">
   <a href="https://github.com/wasi-master/sponsorblock.py/graphs/contributors"><img src="https://img.shields.io/github/contributors/wasi-master/sponsorblock.py.svg?style=flat" alt="Contributors"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/network/members"><img src="https://img.shields.io/github/forks/wasi-master/sponsorblock.py.svg?style=flat" alt="Forks"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/stargazers"><img src="https://img.shields.io/github/stars/wasi-master/sponsorblock.py.svg?style=flat" alt="Stargazers"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/issues"><img src="https://img.shields.io/github/issues/wasi-master/sponsorblock.py.svg?style=flat" alt="Issues"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py"><img src="https://img.shields.io/github/languages/code-size/wasi-master/sponsorblock.py.svg?style=flat" alt="Code Size"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/blob/master/LICENSE"><img src="https://img.shields.io/github/license/wasi-master/sponsorblock.py.svg?style=flat" alt="MIT License"></a>
   <a href="https://saythanks.io/to/arianmollik323@gmail.com"><img src="https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg" alt="Say Thanke"></a>
   <a href="https://pypistats.org/packages/sponsorblock.py"><img src="https://img.shields.io/pypi/dm/sponsorblock.py.svg?style=flat" alt="Downloads last Month"></a>
   <a href="https://pypistats.org/packages/sponsorblock.py"><img src="https://img.shields.io/pypi/dw/sponsorblock.py.svg?style=flat" alt="Downloads last Week"></a>
   <a href="https://pypistats.org/packages/sponsorblock.py"><img src="https://img.shields.io/pypi/dd/sponsorblock.py.svg?style=flat" alt="Downloads last Day"></a>
   <a href="https://pypi.org/project/sponsorblock.py/#history"><img src="https://img.shields.io/pypi/v/sponsorblock.py.svg" alt="Version"></a>
   <a href='https://sponsorblockpy.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/sponsorblockpy/badge/?version=latest' alt='Documentation Status' /></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/actions/workflows/python-app.yml"><img src="https://img.shields.io/github/workflow/status/wasi-master/sponsorblock.py/Python%20application.svg?label=tests" alt="Tests"></a>
   <a href="https://github.com/wasi-master/sponsorblock.py/actions/workflows/python-publish.yml"><img src="https://img.shields.io/github/workflow/status/wasi-master/sponsorblock.py/Upload%20Python%20Package.svg?label=build" alt="Build"></a>
   <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

sponsorblock.py is a wrapper for the [SponsorBlock](https://sponsor.ajay.app) [API](https://wiki.sponsor.ajay.app/index.php/API_Docs)

### Built With

* [python](https://www.python.org)

<!-- GETTING STARTED -->
## Getting Started

To install sponsorblock.py:

### Prerequisites

You'll need to have [python](https://www.python.org) installed in order to use the extension

### Installation

* Installing via pip
  1. Directly installing via pip (Recommended)

     ```sh
     pip install sponsorblock.py
     ```

  2. Installing using pip and git

     ```sh
     pip install git+https://github.com/wasi-master/sponsorblock.py.git
     ```

* Cloning then installing
  1. Clone the repo

     ```sh
     git clone https://github.com/wasi-master/sponsorblock.py.git
     ```

  2. Changing the current working directory to the directory of the project

     ```sh
     cd sponsorblock.py
     ```

  3. Install using pip

     ```sh
     pip install .
     ```

<!-- USAGE EXAMPLES -->
## Usage

See the [documentation](https://sponsorblockpy.readthedocs.io/en/latest/)

There is also a cli that you can use to get segments from the command line (beta).\
To use that run `sponsorblock video_id` and pass your desired video_id

## Roadmap

See the [todo list](https://github.com/wasi-master/sponsorblock.py/blob/main/TODO.md) for a list of features yet to be added and features already added.
Also see the [open issues](https://github.com/wasi-master/sponsorblock.py/issues) for issues.

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/wasi-master/sponsorblock.py](https://github.com/wasi-master/sponsorblock.py)

Discord: [Wasi Master#6969](https://discord.com/users/723234115746398219)

Email: [arianmollik323@gmail.com](mailto:arianmollik323@gmail.com)
