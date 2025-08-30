# Dddit Client

<p align="center"><img src='https://i.postimg.cc/QxnvK4LL/dddit-upscaled.png' alt="Quixel_Texel_Logo" height="400"></p>

## 👋 Author

**Angelo Antonio Prisco** - [AngeloAntonioPrisco](https://github.com/AngeloAntonioPrisco)  

At the moment, I am the only contributor to this project.  
I am a student at **University of Salerno (UNISA)**, currently enrolled in the Master's program in **Software Engineering**.

## 📌 What is it?

**Dddit Client** is the official **Python** client that implements a CLI to consuming the Dddit server's functionalities.
Currently, it supports:

- **FBX models** versioning
- **Materials** versioning, understood as sets of PNG textures  

Main features include:
- Creating and managing **repositories**  
- Handling **resources**, **branches**, and **versions**  
- Each version includes **author**, **comment** and additional metadata  
- A **repository invitations system** to enable collaboration among multiple users on the same repo

## 🚀 How to try it

The client is intended to be built as a standalone *.exe*, but it can also be executed directly in **PyCharm**.

### Build and run the .exe
1. Clone the repository:
   ```bash
   git clone https://github.com/AngeloAntonioPrisco/ddditclient.git
   ```

2. Open the project in PyCharm.

3. Open the PyCharm terminal and run:
    ```bash
    pyinstaller --onefile cli.py
    ```

4. After building, start the generated *.exe* file located in the `dist/` folder.

### Run locally
1. Clone the repo:
   ```bash
   git clone https://github.com/AngeloAntonioPrisco/ddditclient.git
   ```

2. Open the project in PyCharm.

3. Select `CLI.py` and start execution using the Run/Debug configuration.

## 🧱 Built With

- [Python](https://www.python.org/) – Programming language used for the client application.  
- [Typer](https://typer.tiangolo.com/) – Library for building command-line interfaces in Python.  
- [Rich](https://github.com/Textualize/rich) – Library for rich text and formatting in the terminal.  
- [Prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) – Library to build interactive command-line applications.  
- [JWT (JSON Web Tokens)](https://jwt.io/) – Used for authentication with the Dddit Server.


## 🔗 Related resources
- [Dddit Server](https://github.com/AngeloAntonioPrisco/ddditserver): The official Java server for interact with the client.
- [Dddit AI](https://github.com/AngeloAntonioPrisco/ddditai): The official project tha manage Dddit AI module loaded on Dddit Server.
