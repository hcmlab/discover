# Installation

## Prerequesites

Before starting to install DISCOVER you need to install Python and FFMPEG.
While other Python versions may work as well the module is only tested for the following versions:

* 3.9.x
* 3.10.x
* 3.11.x

You can download the current version of python for your system [here](https://www.python.org/downloads/).

Download the current version off FFMPEG binaries from [here](https://github.com/BtbN/FFmpeg-Builds/releases) for your system and make sure to extract them to a place that is in your system path.
It is recommended to setup a separate virtual environment to isolate the NOVA server installation from your system python installation. 
To do so, open a terminal at the directory where your virtual environment should be installed and paste the following command: 

```python -m venv nova-server-venv```

You can then activate the virtual environment like this: 

```.\discover-venv\Scripts\activate```


## Setup

Install DISCOVER using pip like this:

```pip install hcai-discover```

## Start the server

To start DISCOVER you just open a Terminal and type 

```discover```


DISCOVER takes the following optional arguments as input:

```--env```: ```''``` : Path to a dotenv file containing your server configuration

```--host```: ```0.0.0.0``` : The IP for the Server to listen

```--port``` : ```8080``` : The port for the Server to be bound to

```--cml_dir``` : ```cml``` : The cooperative machine learning directory for Nova 

```--data_dir``` : ```data``` : Directory where the Nova data resides

```--cache_dir``` : ```cache``` : Cache directory for Models and other downloadable content 

```--tmp_dir``` : ```tmp``` : Directory to store data for temporary usage  

```--log_dir``` : ```log``` : Directory to store logfiles.

Internally DISCOVER converts the input to environment variables with the following names:
```DISCOVER_HOST```, ```DISCOVER_PORT```, ```DISCOVER_CML_DIR```, ```DISCOVER_CML_DIR```, ```DISCOVER_CML_DIR```, ```DISCOVER_CML_DIR```, ```DISCOVER_CML_DIR```


All variables can be either passed directly as commandline argument, set in a [dotenv](https://hexdocs.pm/dotenvy/dotenv-file-format.html) file or as system wide environment variables.
During runtime the arguments will be prioritized in this order commandline arguments -> dotenv file -> environment variable -> default value.

If the server started successfully your console output should look like this: 

```
Loading environment from /my/path/to/.env
	#DISCOVER Config
	DISCOVER_HOST: 127.0.0.1
	DISCOVER_PORT: 37317
	DISCOVER_CML_DIR: /cml
	DISCOVER_DATA_DIR: /data
	DISCOVER_CACHE_DIR: /cache
	DISCOVER_TMP_DIR: /tmp
	DISCOVER_LOG_DIR: /log
	DISCOVER_BACKEND: venv
	DISCOVER_VIDEO_BACKEND: IMAGEIO
```

