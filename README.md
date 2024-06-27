
Robot's Inner Speech and Damasio's Theory of Emotions
===========================================

The repository was built as additional material of the paper entitled
"Inner Speech and Damasio’s Theory for Modelling
Robot’s Emotions" by Sophia Corvaia, Arianna Pipitone and Antonio Chella .

The framework provides the robot with the ability to interpret the context through inner speech (the self-dialogue implemented by the inner speech cognitive architecture [1]) and to elicit an emotion based on this interpretation. The emotion emerges by projecting the interpreted variables (mathematically formalized as described in the paper) into Russell's space, in accordance with Antonio Damasio's theory of emotions.

The repository contains the Python scripts implementing the proposed model of the tight link between inner speech and emotions, and the needed resources for running it (the knowledge model and the xml description of the parameters for the appraisal variables).
 
Please, refer to the paper for more details, and to the files in the <b>module</b> folder of this repository for comments about the code.

To run the provided framework, the NaoQi 2.5 have to be installed, and you can deploy the code on the robots by Aldebaran, specifically Pepper or NAO. Not other robotics platforms are tested.

[1] Pipitone A., Chella A. What robots want? Hearing the inner voice of a robot
iScience, Volume 24, Issue 4, 2021, Article 102371

Running the model on real robot
==========================================

Prerequisites
-------------

Operative systems:

- Ubuntu 20.04 LTS or latest

- Windows with Windows Subsystem for Linux (WSL) with Ubuntu 20.04 LTS or latest 
(you can follow the official instructions available at <https://docs.microsoft.com/en-us/windows/wsl/install-manual> for enabling WSL)

1 Prepare the environment
-------------------------

- Install additional libraries

- <b>NAOqi</b>: The project require the Naoqi library to manage robot of Aldebaran. 


    pip install naoqi

You can follow the instruction available at <http://doc.aldebaran.com/2-5/dev/python/install_guide.html>. You have to check your NAOqi version on your robot before doing the installation.

### 1.1 Setting up the Knowledge
If you want to change the ontology in the project, you may change the file at:

    /resources/knowledge/onto_music.owl
Pay attention: the project requires an OWL ontology file to be execute.

### 1.2 Setting up the Emotion Body reactions
The project evaluate reactions of the 5 primary emotions Ekman's theory. 
You need to set up the csv emotions by executing the emo_body.py file. 
After that, you will find the evaluated emotions at:

 
    /resources/data/emBody_value.csv
    /resources/data/emBody_color.csv
You can select the emotion you interest and run the project.

2 Run the middleware
----------------------------------
Launch the script project by the following command:

    python main.py
    
and see your Pepper/NAO robot interacts to you while reasoning about its emotion by inner speech. 

Please, pay attention to the argument passed to the function.

Enjoy!









