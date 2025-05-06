# AI 3-in-1 
## An overview of Running Models Locally, AI Agents, and RAG
## User guide 
## Revision 1.0 - 05/05/25

**Setup**
Follow the steps outlined in the [**README.md**](./README.md) file to get setup with your own [**codespace**](https://github.com/features/codespaces) environment to run the examples in. 

The startup process should set you up with a Python runtime environment and download the llama3.2 AI model for you to use in the codespace.
<br><br><br>

**Part A. What's in this repository**

1. In this repository, you can find the example files shared at the meetup to do very simple illustrations of the concepts.

<br>

2. In the **code** directory are the 3 example files:

- *local.py* - A simple app that connects to the locally running llama3.2 instance (served by Ollama) and allows you to prompt it. Type *exit* to exit.
- *agent.py* - The simple app plus some extra tools for computing distance from a known location to illustrate how agents work.
- *rag.py* - The agent app plus code to read in a PDF file, store it in a vector database, query it for a match, and then send that to the LLM. Illustrates how RAG works.

<br>

3. In the **charts** directory are 3 charts in [**Mermaid**](https://www.mermaidchart.com/) format. These are 3 flowcharts that are intended to help show the logic/flow of each example. (Some text may be cut off.)

- *local.md* - corresponds to the local.py flow
- *agent.md* - corresponds to the agent.py flow
- *rag.md* - corresponds to the rag.py flow 

<br>

4. In the **data** directory:

- *offices.pdf* - pdf table with office location information for use as data in the rag.py example
- *requirements.txt* - python dependencies to install

<br>

5. In the **scripts** directory:

- *pysetup.sh* - run automatically at startup to setup Python environment
- *startOllama.sh* - run automatically at startup to bootstrap Ollama (linux setup) and download model

**NOTE** If you run into issues with the Python environment or Ollama setup, you can try running these yourself.

<br>

6. In the **images** directory are some images used in the various docs.
<br><br><br>

**Part B: Running the examples**

1. Get your codespace or local environment setup.

<br>

2. Change into the *code* subdirectory.
```
cd code
```

<br>

3. Execute the code via python
```
python <filename>.py
```

<br>

4. At the prompt, you can ask the app about a particular location. If you are using the *RAG* example (rag.py), you can ask using a term or keyword that is in the PDF file. (Examples shown below.)

![Running the agent example](./images/3in1f.png?raw=true "Running the agent example")

![Running the rag example](./images/3in1e.png?raw=true "Running the rag example")

<br><br><br>

**Part C: Seeing changes between files.**

1. To see the changes between the local version and the agent version, you can use the following command if you're in the codespace or if you are in a *VS Code* IDE environment.

```
cd code <if not there already>
code -d local.py agent.py
```

<br>

2. To see the changes between the agent version and the rag version, you can use the following command iff you're in the codespace or if you are in a *VS Code* IDE environment.

```
cd code <if not there already>
code -d agent.py rag.py
```
<br><br><br>

**Part D: Troubleshooting**

1. If you run into issues with running Python, try running the *scripts/pysetup.sh* script.

<br>

2. If you run into issues with Ollama not working, try running the *scripts/startOllama.sh* script. Note this is setup for Linux environments. If you need to run Ollama on a different platform, consult the documentation at Ollama.com.

<br>

3. If you can't see the Mermaid charts, install a Mermaid viewer. (The Codespace already includes an installed extension for this.)

<br>

<p align="center">
**[END OF GUIDE]**
</p>
<p align="center">
(c) 2025 Tech Skills Transformations & Brent Laster
</br></br></br>

