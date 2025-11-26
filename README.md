# DISCOVER - A Modular Software Framework for Human Behavior Analysis


## Overview

DISCOVER is an open-source software framework designed to facilitate computational-driven data exploration in human behavior analysis. This user-friendly and modular platform streamlines complex methodologies, enabling researchers across disciplines to engage in detailed behavioral analysis without extensive technical expertise.

Key Features

* Modularity: DISCOVER's modular architecture allows for easy integration of new features and customization.
* User-Friendliness: Intuitive interface simplifies the data exploration process, making it accessible to non-technical users.
* Flexibility: Supports a wide range of data types and analysis workflows.
* Scalability: Handles large datasets with ease.

Use Cases

* Interactive Semantic Content Exploration
* Visual Inspection
* Aided Annotation
* Multimodal Scene Search

## Getting Started

DISCOVER provides a set of blueprints for exploratory data analysis, serving as a starting point for researchers to engage in detailed behavioral analysis.

### Prerequesites

Before starting to install DISCOVER you need to install Python and FFMPEG.
DISCOVER is currently developed and tested on:

* Python 3.12.x
* Ubuntu Linux

While other Python versions and operating systems may work, they are not actively tested or supported.

You can download the current version of python for your system [here](https://www.python.org/downloads/).

Download the current version off FFMPEG binaries from [here](https://github.com/BtbN/FFmpeg-Builds/releases) for your system and make sure to extract them to a place that is in your system path.

### Recommended Installation on Windows: Using WSL

For Windows users, we strongly recommend installing DISCOVER using Windows Subsystem for Linux (WSL) instead of native Windows installation. This approach provides better compatibility and avoids common issues with package compilation.

**Setting up WSL:**

1. Install WSL 2 by opening PowerShell as Administrator and running:
   ```
   wsl --install
   ```

2. After installation, open your WSL terminal (Ubuntu or your chosen distribution).

3. Install the required system packages for building the `av` package and its dependencies:
   ```bash
   sudo apt update
   sudo apt install ffmpeg python3-dev build-essential
   ```

4. Install Python (if not already installed):
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

5. Continue with the Setup instructions below within your WSL environment.

### Virtual Environment Setup

It is recommended to setup a separate virtual environment to isolate the DISCOVER installation from your system python installation.
To do so, open a terminal at the directory where your virtual environment should be installed and paste the following command:

```python -m venv discover-venv```

You can then activate the virtual environment like this:

**Linux/macOS/WSL:**
```source discover-venv/bin/activate```

**Windows (native):**
```.\discover-venv\Scripts\activate```

### Setup

Install DISCOVER using pip like this:

```pip install hcai-discover```

### Start the server

To start DISCOVER you just open a Terminal and type

```discover```

DISCOVER takes the following optional arguments as input:

```
--env: '' : Path to a dotenv file containing your server configuration

--host: 0.0.0.0 : The IP for the Server to listen

--port : 8080 : The port for the Server to be bound to

--cml_dir : cml : The cooperative machine learning directory containing DISCOVER modules (available at: https://github.com/hcmlab/discover-modules)

--data_dir : data : Directory where the data resides

--cache_dir : cache : Cache directory for Models and other downloadable content

--tmp_dir : tmp : Directory to store data for temporary usage

--log_dir : log : Directory to store logfiles.

--use_tls : Enable TLS/SSL for HTTPS connections (requires certificates)
```

Internally DISCOVER converts the input to environment variables with the following names: 

```DISCOVER_HOST```, ```DISCOVER_PORT```, ```DISCOVER_CML_DIR```, ```DISCOVER_DATA_DIR```, ```DISCOVER_CACHE_DIR```, ```DISCOVER_TMP_DIR```, ```DISCOVER_LOG_DIR```, ```DISCOVER_USE_TLS```


All variables can be either passed directly as commandline argument, set in a [dotenv](https://hexdocs.pm/dotenvy/dotenv-file-format.html) file or as system wide environment variables.
During runtime the arguments will be prioritized in this order commandline arguments -> dotenv file -> environment variable -> default value.

If the server started successfully your console output should look like this:
```
Starting DISCOVER v1.0.0...
HOST: 0.0.0.0
PORT: 8080
DISCOVER_CML_DIR : cml
DISCOVER_DATA_DIR : data
DISCOVER_CACHE_DIR : cache
DISCOVER_TMP_DIR : tmp
DISCOVER_LOG_DIR : log
...done
DISCOVER HTTP server starting on 0.0.0.0:8080
```

### Job Management

DISCOVER includes a web-based job management interface accessible at the root URL (e.g., `http://localhost:8080` or `https://localhost:8080` with TLS enabled). This interface allows you to:

* Monitor all running, pending, and completed jobs
* View which module is being used for each job
* Track session progress (e.g., "2/5" sessions completed)
* Cancel running or queued jobs
* Access job logs for detailed information

Jobs that are manually canceled will display a gray "Canceled" button in the Actions column, allowing you to distinguish between naturally failed jobs and those that were canceled by the user.

### Modules

DISCOVER modules contain the machine learning models and processing pipelines. You can get the official modules from:

**https://github.com/hcmlab/discover-modules**

Clone or download the modules repository and set the `--cml_dir` parameter to point to the modules directory.

You can find the full documentation of the project [here](https://hcmlab.github.io/discover).

## Citation
If you use DISCOVER consider citing the following paper:

```
@article{hallmen2025discover,
  title={DISCOVER: a Data-driven Interactive System for Comprehensive Observation, Visualization, and ExploRation of human behavior},
  author={Hallmen, Tobias and Schiller, Dominik and Vehlen, Antonia and Eberhardt, Steffen and Baur, Tobias and Withanage, Daksitha and Lutz, Wolfgang and Andr{\'e}, Elisabeth},
  journal={Frontiers in Digital Health},
  volume={7},
  pages={1638539},
  publisher={Frontiers}
}
```