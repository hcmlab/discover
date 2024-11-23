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
We already decided to use the WhisperX module to create the transcript. 
Therefore, we first take a quick look at the modules [documentation](https://hcmlab.github.io/discover/modules/whisperx.html#) to learn about the required inputs and outputs for the model.

Under th `IO` section of the module the documentation states the following

```
IO

Explanation of inputs and outputs as specified in the trainer file:

Input

audio (Audio): The input audio to transcribe

Output

The output of the model:

transcript (FreeAnnotation): The transcription
```

Which means that we need to pass an input of type `Audio` and specify a `FreeAnnotation` to write the transcript to. 

In our example we assume that you already have a NOVA database containing audio files for which you want to calculate the transcript. 
So there for all we need to prepare is the output annotation for the transcript. 
To this end we create a new annotation scheme in the NOVA database. 
In NOVA click on `DATABASE` -> `Administration` -> `Manage Databases`. 
Select the database you want to work with in the left column and click the `add` button at the bottom of the `Schemes` column.
Next select the `Create scheme with custom labels` option and hit next. 
Finally provide a fitting name to scheme (e.g. transcript) and hit `ok`. 


### 3. The DISCOVER interface explained
Now that we are done with our database preparation we can finally calculate the transcript.
Click on `LEARNING` -> `DISCOVER Server` in NOVA and you will see the following window: 

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/discover_module?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/discover_module.png?raw=true" alt="Alt Text" width="500" height="300"></a>


Select the respective dataset (1) in the left column. 
The `Processor` column (2) shows all modules that are available on you DISCOVER server instance.
Select `WhisperX`. 
Column `Inputs` (3) provides you a selection of all streams in your database that are matching the input requirements of `WhisperX`.
Since `WhisperX` requires a single Audio file as input you should see all audio streams that are associated with the selected dataset.
Select the fitting stream and role for which you want to extract the transcript.
Analogously the `Output` column let you select a fitting output annotation scheme, role and annotator for which `WhisperX` should create the transcript in the database. 
Select the Free annotation scheme that we created in step 2, the same role as for the input and an arbitrary annotator. 
Just remember the name :) 
Finally, in the bottom right window you can select various options for the selected module. 
For a detailed explanation of the options refer to the [documentation](https://hcmlab.github.io/discover/modules/whisperx.html#) of the module.

### 4. Calculating the transcript
Once you are satisfied with your selection hit `Send`. 
Now the text in the bottom left should change to "Process running..." and you should start to see logging output in the log window above the option window on the right side.
You can now leave NOVA or wait till the process is finished. 
If you want to get information about the current status of the transcript processing you just need to reopen the `DISCOVER server` window in  NOVA and select the same settings.
Once the job is done you can load the transcript annotation using `DATABASE` -> `Load Session` and select the respective scheme, role and annotator you specified earlier. 
