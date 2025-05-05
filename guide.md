# AI 3-in-1 
## An overview of Running Models Locally, AI Agents, and RAG
## User guide 
## Revision 1.0 - 05/05/25

**Setup**
Follow the steps outlined in the [**README.md**](./README.md) file to get setup with your own [**codespace**](https://github.com/features/codespaces) environment to run the examples in. 

The startup process should set you up with a Python runtime environment and download the llama3.2 AI model for you to use in the codespace.

**Part A. What's in this repository**

1. In this repository, you can find the example files shared at the meetup to do very simple illustrations of the concepts.

2. In the **code** directory are the 3 example files:

- *local.py* - A simple app that connects to the locally running llama3.2 instance (served by Ollama) and allows you to prompt it. Type *exit* to exit.
- *agent.py* - The simple app plus some extra tools for computing distance from a known location to illustrate how agents work.
- *rag.py* - The agent app plus code to read in a PDF file, store it in a vector database, query it for a match, and then send that to the LLM. Illustrates how RAG works.

3. In the **charts** directory are 3 charts in [**Mermaid**](https://www.mermaidchart.com/) format. These are 3 flowcharts that are intended to help show the logic/flow of each example. (Some text may be cut off.)

- *local.md* - corresponds to the local.py flow
- *agent.md* - corresponds to the agent.py flow
- *rag.md* - corresponds to the rag.py flow 
   
4. In the **data** directory:

- *offices.pdf* - pdf table with office location information for use as data in the rag.py example
- *requirements.txt* - python dependencies to install

5. In the **scripts** directory:

- *pysetup.sh* - run automatically at startup to setup Python environment
- *startOllama.sh* - run automatically at startup to bootstrap Ollama (linux setup) and download model

**NOTE** If you run into issues with the Python environment or Ollama setup, you can try running these yourself.

6. In the **images** directory are some images used in the various docs.

**Part B: Running the examples**

1. Get your codespace or local environment setup.

2. Change into the *code* subdirectory.
```
cd code
```

3. Execute the code via python
```
python <filename>.py
```

4. At the prompt, you can ask the app about a particular location. If you are using the *RAG* example (rag.py), you can ask using a term or keyword that is in the PDF file.

**Part C: Seeing changes between files.**

1. To see the changes between the local version and the agent version, you can use the following command if you're in the codespace or if you are in a *VS Code* IDE environment.

```
cd code <if not there already>
code -d local.py agent.py
```

2. To see the changes between the agent version and the rag version, you can use the following command iff you're in the codespace or if you are in a *VS Code* IDE environment.

```
cd code <if not there already>
code -d agent.py rag.py
```

**Part D: Troubleshooting**

1. If you run into issues with running Python, try running the *scripts/pysetup.sh* script.

2. If you run into issues with Ollama not working, try running the *scripts/startOllama.sh* script. Note this is setup for Linux environments. If you need to run Ollama on a different platform, consult the documentation at Ollama.com.

3. 



  6. Adjust codespace timeout via README instructions. If your codespace does time out, just run the *setup.sh* script again after restarting it. 

8. To copy and paste in the codespace, Chrome is recommended. You may need to use keyboard commands - CTRL-C and CTRL-V.**

<br><br>

**Lab 1 - Building Docker Images**

**Purpose: In this lab, we’ll see how to build Docker images from Dockerfiles.**
<br><br>

1. Switch into the directory for our docker work.

```
cd roar-docker
```
<br>

2. Take a look at the "Dockerfiles" that we have in this directory and see if you can understand what's happening in them. 

   a. Click on the link or, in the file explorer to the left, select the file [**roar-docker/Dockerfile_roar_db_image**](./roar-docker/Dockerfile_roar_db_image)
   
   b. Click on the link or, in the file explorer to the left, select the file [**roar-docker/Dockerfile_roar_web_image**](./roar-docker/Dockerfile_roar_web_image) 

<br>

3. Now let’s build our docker database image. Type (or copy/paste) the following
command: (Note that there is a space followed by a dot at the end of the
command that must be there.)

```
docker build -f Dockerfile_roar_db_image -t roar-db .
```

<br>

4. Next build the image for the web piece. This command is similar except it
takes a build argument that is the war file in the directory that contains our
previously built webapp.

(Note the space and dot at the end again.)

```
docker build -f Dockerfile_roar_web_image --build-arg warFile=roar.war -t roar-web .
```

<br>

5. Now, let’s tag our two images for our local registry (running on localhost, port
5000). We’ll give them a tag of “v1” as opposed to the default tag that Docker
provides of “latest”.

```
docker tag roar-web localhost:5000/roar-web:v1
docker tag roar-db localhost:5000/roar-db:v1
```

<br>

6. Do a docker images command to see the new images you’ve created.
```
docker images | grep roar
```
<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2 - Composing images together**

**Purpose: In this lab, we'll see how to make multiple containers execute together with docker compose and use the docker inspect command to get information to see our running app.**
<br><br>

1. Take a look at the docker compose file for our application and see if you can understand some of what it is doing. Click on the link: [**roar-docker/docker-compose.yml**](./roar-docker/docker-compose.yml) 
<br>

2. Run the following command to compose the two images together that we built in lab 1.

```
docker compose up
```
<br>

3. You should see the different processes running to create the containers and start the application running. In order to do the following steps, we'll need to open a second terminal. We can do that by splitting this one. Either right-click and select *Split Terminal* or click on the two-panel icon near the trash can. See screenshot.

![Adding a second split terminal](./images/lab2s3.png?raw=true "Splitting the terminal")

<br>

4. Click in the second terminal and take a look at the running containers that resulted from the docker compose command by running the command below.

```
docker ps | grep roar
```

<br>

5. Make a note of the first 3 characters of the container id (first column) for the web container (row with roar-web in it). You’ll need those for the next lab.

![Container id for web container](./images/cazclass19.png?raw=true "Container id for web container")

<br>

6. Let’s see our application running from the containers and the compose. In the top "tab" line of the terminal, click on the *PORTS* tab. Per the docker-compose.yml file, our web app is running on port 8089. Find the row (probably the 2nd or 3rd row) with "8089" in the *Port* column. Under the second column *Forwarded Address*, click on the icon that looks like the splitter pane and, when you hover over it, says **Preview in Editor**. (See screenshot below.)
   
![Opening preview of app in editor](./images/lab2s5.png?raw=true "Opening preview app in editor")

<br>

7. After this, you should get a simple browser that opens up as a pane in the editor.

![Preview of server in editor](./images/lab2s6.png?raw=true "Preview of server in editor")

<br>

8. To see our app, we need to add **/roar/** to the end of the URL in that simple browser window. Do that now - you must have the trailing slash!

![App in editor](./images/lab2s7.png?raw=true "App in editor")   

<br>

9. You should see the running app in the window, though you may need to scroll around  or expand the window to see all of it.

![Full app](./images/lab2s8.png?raw=true "Full app")   

<br>

10. Switch back to the Terminal tab for the next lab.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 3 – Debugging Docker Containers**

**Purpose: While our app runs fine here, it’s helpful to know about a few commands that we can use to learn more about our containers if there are problems.**
<br><br>

1. (We're back in the second terminal with the compose still running in the first terminal.) Let’s get a description of all of the attributes of our containers. For these commands, use the same 3 character container id from the web container that you recorded from Lab 2, step 5 and run them in the second terminal window (the one that is not running the docker compose as that needs to stay running during these).
   
Run the inspect command. Take a moment to scroll around the output.

```
docker inspect <container id>
```
<br>

2. Now, let’s look at the logs from the running container. Scroll around again and look at the output.

```
docker logs <container id>
```

<br>

3. While we’re at it, let’s look at the history of the image (not the container).

```
docker history roar-web
```

<br>

4. Now, let’s suppose we wanted to take a look at the actual database that is
being used for the app. This is a mysql database but we don’t have mysql
installed on the VM. So how can we do that? Let’s connect into the container
and use the mysql version within the container. To do this we’ll use the “docker
exec” command. First find the container id of the db container.

```
docker ps | grep roar-db
```

<br>

5. Make a note of the first 3 characters of the container id (first column) for the db
container (row with **roar-db** in it). You’ll need those for the next step.

![Container id for db container](./images/cazclass20.png?raw=true "Container id for db container")
<br>

6. Now, let’s exec inside the container so we can look at the actual database.

```   
docker exec -it <container id> bash
```
Note that the last item on the command is the command we want to have
running when we get inside the container – in this case the bash shell.

<br>

7. Now, you’ll be inside the database container. Check where you are with the pwd
command and then let’s run the mysql command to connect to the database.
(Type these at the /# prompt. Note no spaces between the options -u and -p
and their arguments. You need only type the part in bold.)
