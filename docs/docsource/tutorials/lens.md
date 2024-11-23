# LENS: Learning and Exploring through Natural language Systems

LENS is lightweight webserver designed to use Large Language Models as tool for data exploration in human interactions.
In this tutorial we show how LENS can be used in conjunction to with the [NOVA](https://github.com/hcmlab/nova) user interface and the [DISCOVER](https://github.com/hcmlab/discover) server to explore and categorize textual data.

## Overview

First let's make sure to establish a common understanding of the interplay between NOVA, DISCOVER and LENS.
NOVA is the user interface to interact with all other services. While NOVA can be used as a standalone tool to visualize and annotated multimodal data streams it also has the built-in ability to communicate with LENS and DISCOVER servers using their respective apis.

DISCOVER serves as a computational backend to extract features or infer annotations from multimodal data using predefined modules. For example such modules can be used to detect faces in images or create a transcript from an audio signal.
Since modules all need to implement a common interface, it is straight forward to write your own modules and provide them to others. All modules are producing either annotations or datastreams that can be later visualized in the NOVA user interface.
DISCOVER also works in tandem together with the NOVA annotation database. Annotations can therefore be directly written to or read from this database to enable coherent data management and easy sharing of results among all database users.

LENS is lightweight webserver that provides a unified API to contact multiple LLMs using the same request format. This includes local instances such as [Ollama](https://ollama.com) or webservices such as [ChatGPT](https://chatgpt.com). 
This api is also integrated in the NOVA user interface to enable a seamless interaction with text annotations from within NOVA.

In the following we will demonstrate the interaction between those three tools using three exemplary use cases. 


## Prerequisites

For all the following use cases we assume that you already have NOVA, DISCOVER and LENS installed.
Refer to the following documentations if this is not the case: 
* [NOVA Documentation](https://rawgit.com/hcmlab/nova/master/docs/index.html)
* [DISCOVER Documentation](https://hcmlab.github.io/discover/tutorials/introduction.html#getting-started)
* [LENS Documentation](https://github.com/hcmlab/lens)

Once the three services are up and running we first need to connect NOVA to DISCOVER and LENS. 
To this end open NOVA and click on the gear icon in the top left corner. 
In the settings menu you should see two tabs DISCOVER and LENS.

For the DISCOVER settings you only need to insert the host ip address and the port number that you used to start the DISCOVER Server  

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_discover.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_discover.png?raw=true" alt="Alt Text" width="500" height="200"></a>


In the LENS settings page you can specify more parameters that are relevant to how the LLMs behind LENS should interact with the data.
For an explanation of the individual parameters refer to [the LENS github repository](https://github.com/hcmlab/lens?tab=readme-ov-file#api).
You will find an explanation for each parameter in the API section under `POST /assist`.

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_lens.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/nova_lens.png?raw=true" alt="Alt Text" width="500" height="300"></a>

## Usage

Now that we have installed all the tools necessary we can start to explore our data in NOVA. 
To this end we will use a mockup therapy session interaction as a running example. 
You can download the transcript in the NOVA annotation format [here]()

### Interactive data exploration

The most straight forward use case to interact with lens is by chatting with it. 
To this end you can just hit the LENS tab on the right side of the NOVA tab bar or press `ctrl + a` in NOVA.

In the upcoming chat window you will see a textbar where you can ask your questions to LENS a model selection drop down menu to select the model you want to interact with and `Context-Aware` checkbox.  
If you check this box NOVA will automatically attach all currently opened Free and Discrete annotations to the message.

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/lens_window.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/lens_window.png?raw=true" alt="Alt Text" width="500" height="200"></a>

For example if you want to analyze the contents of our demo transcript you can just open it in NOVA and start asking LENS about the contents of the transcript.

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/lens_chat.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/lens_chat.png?raw=true" alt="Alt Text" width="500" height="400"></a>

Keep in mind that the roles and sequential order of the opened annotations will be guaranteed but no specific time-information is provided to the LENS.
For example The request created by NOVA could look like this.
```

{
    'system_prompt': "Your name is Nova Assistant. You are an AI assistant. Keep your answers short, don't repeat yourself and if you do no know the answer don't make it up.", 
    'data': 
        [
            {
                'role': 'system', 
                'content': 'Your name is LENS. You are an AI assistant. Keep your answers short, don\'t repeat yourself and if you do no know the answer don\'t make it up.
                (therapeut,"Okay, so this is our first session after the holidays now and I just wanted to chat with you about the holidays and what you experienced during the days.");
                (patient,"Happy New Year.");(patient,"So it started very nicely with seeing my family again after a long time since I live so far from home.");
                (patient,"It\'s nice to come back and to see everyone again and to, I don\'t know, just to have the time and talk and eat and drink and just");
                (patient,"I don\'t know, play games and be around each other and yeah, just...);
                (therapeut,"So you were able to enjoy the time with your family?");
                (patient,"Yes.");(patient,"No, it was very nice seeing everyone and just, yeah, in between things just to have some time the whole day and to, yeah, talk to each other and just be there and relax.");
                (patient,"Yeah.")
                ...
            }
        ],
        'model': 'llama3.2:latest', 
        'provider': 'ollama', 
        'message': 'summarize the transcript', 
        'temperature': 1.0, 
        'num_ctx': 10000, 
        'max_new_tokens': 1024, 
        'top_p': 0.95, 
        'top_k': 50, 
        'history': [], 
        'enforce_determinism': True
}
```


### LENS via DISCOVER

Another way to interact with LENS is by using the [DISCOVER module](https://github.com/hcmlab/discover-modules/tree/main/modules/lens).
With this module DISCOVER uses LENS to automatically create annotations from a provided transcript and a respective prompt.
The LENS module consists of two different functionalities. 
The first one is the `lens_free_prompt` module which works by iterating over the transcript an then applies a user defined prompt to each identified segment.
The second method is the `lens_predcit` module that automatically constructs a prompt to a fit a predefined annotation scheme in nova using information like the name of the labels or a custom description of the labeling scheme.

We are going to start with an example for the `lens_free_prompt` module.
For the first use case we are going to translate the transcript from english to german using llama3.2.
Keep in mind that LENS through DISCOVER only works together with the NOVA database.
Therefore, you will need to import all the transcripts you want to process into the database before using them.


<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/free_prompt.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/free_prompt.png?raw=true" alt="Alt Text" width="1920" height="500">

At first we are going to create a new free annotation scheme in our target database called `llm_translation`. 
To begin with the extraction process we first open the DISCOVER modules in NOVA by clicking on  `LEARNING` -> `DISCOVER Server`. 
In the upcoming window we select our desired database on the left side (1). 
As processor we use the `lens_free_prompt` module (2).
In the input section (3) we select the transcript we want to translate as well as the role and annotator who created original transcript.
In the ouput section (4) we select out `llm_translation` scheme as output using the same role as the input and an annotator of our own choice. 
In the session selection window (5) select the sessions you want to process. 
Finally in the options window (6) we specify all options that we need to pass to the DISCOVER [LENS](https://github.com/hcmlab/discover-modules/tree/main/modules/lens) module.
Specify the ip and the port under which the LENS server is reachable. 
Specify the provider and and the model you want to use. If you are unsure which models are supported by your LENS installation you can always check the model selection from the LENS chat window in NOVA.
In the prompt window we finally type the instruction we want the LLM to apply to each label. In our case type "translate the following text to german".

After the module has finished processing navigate to `Database` -> `Load Session` and select the newly created annotation to verify your results. 

<a href="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/translation.png?raw=true"><img src="https://github.com/hcmlab/discover/blob/documentation/docs/docsource/imgs/translation.png?raw=true" alt="Alt Text" width="1920" height="500"></a>

