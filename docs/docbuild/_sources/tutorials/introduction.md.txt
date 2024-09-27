# Installation

## Prerequesites

Before starting to install NOVA-Server you need to install Python and FFMPEG.
While other Python versions may work as well the module is only tested for the following versions:

* 3.9.x

You can download the current version of python for your system [here](https://www.python.org/downloads/).

Download the current version off FFMPEG binaries from [here](https://github.com/BtbN/FFmpeg-Builds/releases) for your system and make sure to extract them to a place that is in your system path.
It is recommended to setup a separate virtual environment to isolate the NOVA server installation from your system python installation. 
To do so, open a terminal at the directory where your virtual environment should be installed and paste the following command: 

```python -m venv nova-server-venv```

You can then activate the virtual environment like this: 

```.\nova-server-venv\Scripts\activate```


## Setup

Install NOVA-Server using pip like this:

```pip install hcai-nova-server```

## Start the server

To start NOVA-Server you just open a Terminal and type 

```nova-server```


NOVA-Server takes the following optional arguments as input:

```--env```: ```''``` : Path to a dotenv file containing your server configuration

```--host```: ```0.0.0.0``` : The IP for the Server to listen

```--port``` : ```8080``` : The port for the Server to be bound to

```--cml_dir``` : ```cml``` : The cooperative machine learning directory for Nova 

```--data_dir``` : ```data``` : Directory where the Nova data resides

```--cache_dir``` : ```cache``` : Cache directory for Models and other downloadable content 

```--tmp_dir``` : ```tmp``` : Directory to store data for temporary usage  

```--log_dir``` : ```log``` : Directory to store logfiles.

Internally NOVA-Server converts the input to environment variables with the following names:
```NOVA_SERVER_HOST```, ```NOVA_SERVER_PORT```
```NOVA_SERVER_CML_DIR```, ```NOVA_SERVER_CML_DIR```, ```NOVA_SERVER_CML_DIR```, ```NOVA_SERVER_CML_DIR```, ```NOVA_SERVER_CML_DIR```


All variables can be either passed directly as commandline argument, set in a [dotenv](https://hexdocs.pm/dotenvy/dotenv-file-format.html) file or as system wide environment variables.
During runtime the arguments will be prioritized in this order commandline arguments -> dotenv file -> environment variable -> default value.

If the server started successfully your console output should look like this: 

```
Starting nova-backend server...
HOST: 0.0.0.0
PORT: 8080
NOVA_CML_DIR : cml
NOVA_DATA_DIR : data
NOVA_CACHE_DIR : cache
NOVA_TMP_DIR : tmp
NOVA_LOG_DIR : log
...done
```