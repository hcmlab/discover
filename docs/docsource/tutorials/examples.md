# Examples

# Creating a Transcript using NOVA 
DISCOVER is tightly interwoven with the NOVA annotation tool. 
This means you can use NOVA as a graphical user interface to run discover modules on data streams and annotations that you have already integrated into NOVA.
In this example we will illustrate how you can create a transcript from an audio signal for multiple session using the WhisperX module. 
We assume that you have a recent and working version of NOVA running on your system and are familiar with the basic NOVA usage and database navigation.

### 1. Connect Discover
In the first step we need to connect NOVA to DISCOVER. 
To this end open NOVA and click on the gear icon in the top left corner. 
In the settings menu you should see a DISCOVER tab.
Insert the host ip address and the port number that you used to start the DISCOVER Server, hit apply and you are done.

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_discover.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_discover.png?raw=true" alt="Alt Text" width="500" height="200"></a>

### 2. Database preparation 
We already picked our 
In our example we assume that you already have a NOVA database containing audio files for which you want to calculate the transcript. 
However, since NOVA operates on the principle that all 

we still need to define the output   

### 2. The DISCOVER interface explained

Now, when you click on `LEARNING` -> `DISCOVER Server` a window will 