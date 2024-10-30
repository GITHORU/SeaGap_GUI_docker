<a  href="https://githoru.github.io/SeaGap_GUI_docker/">
<p align="center">
  Web view here
</p>
</a>

<p align="center">
　<img src="https://github.com/GITHORU/SeaGap_GUI_docker/blob/main/img/seagap_docker_GUI.png" width="200">
</p>

# SeaGap Docker GUI

This repo contains a GUI for simplifying the usage of F. Tomita's GNSS/A software : SeaGap ! This software, written in Julia, allows to use all the state-of-the-art GNSS/A calculation methods and has been explained in Tomita's 2024 article. 
- [SeaGap repo](https://github.com/f-tommy/SeaGap)
- [SeaGap's documentation](https://f-tommy.github.io/SeaGapDocs/)
- [Tomita's 2024 article](https://earth-planets-space.springeropen.com/articles/10.1186/s40623-024-01987-9)

This repos is meant to increase SeaGap portability by both creating a Docker image and creating a Windows/Linux-friendly GUI, allowing to get rid of Julia’s dependency issues. It also aims at simplifying its usage for users that are not used to Julia at therefore reduce the technological gap between GARPOS, Gnatss and SeaGap. This effort for the unification of GNSS/A treatments is also carried out by the implementation of a GARPOS to SeaGap data converter, allowing the usage of GARPOS datasets with SeaGap.
- [Docker image from DockerHub](https://hub.docker.com/r/githoru/seagap_docker_img)
- [GARPOS dataset](https://zenodo.org/records/3993912)

## Installation
### Docker
Docker is used to create images and containers. Images are templates for creating containers, which are lightweight isolated systems able to run commands and containing libraries present in the image. The image is built from a file named a Dockerfile, which specifies all the actions we want to perform to create the image (installation of libraries, creation of specific paths, commands to run by default ...). Once the image is built, we can use it to create as many containers as we want, without needing to install all the dependencies again, as they are already installed in the image. In our case, the image is already built and can be accessed publicly from [DockerHub](https://hub.docker.com/r/githoru/seagap_docker_img). It contains Julia, with SeaGap already precompiled and ready to be used.

For the GUI to work, you need to install Docker. To do so, follow the procedure explained on the Docker website :
- [For Windows](https://docs.docker.com/desktop/install/windows-install/)
- [For MacOs](https://docs.docker.com/desktop/install/mac-install/)
- [For Linux](https://docs.docker.com/engine/install/) (Specifically for Ubuntu, the "apt" methods explained [here](https://docs.docker.com/engine/install/binaries/) works)

Once docker is correctly installed, you will be able to pull SeaGap_docker_img image by running :
```
docker pull githoru/seagap_docker_img
```

If you encounter permission issues on Linux, a solution is to run the following commands in order to give permission to docker :
```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

Then reboot your system. Docker pull should then work.

Note that if you do not pull the image, the GUI will download it by itself and might seem laggy for a while on the first launch. It is therefore recommended to pull it by yourself.

### Python
It is recommended to create a specific virtual env for the GUI. To do so, open a terminal in the SeaGap_GUI_docker folder and then run :
```
pip install virtualenv
python -m venv ./venv
```

To activate it run :
- Linux :
  ```
  source venv/bin/activate
  ```
- Windows :
  ```
  .\venv\Scripts\activate
  ```
To install python dependencies :
```
pip install -r requirements.txt
```

### Running
With the python of env of your choice activated, as long as the dependencies are correctly installed, you can now run the GUI from the src folder by typing :
```
python gui.py
```

## Why Docker

There are four main issues with Julia :
- 1 : The way Julia packages are installed requires a long installation time for the first install
  
- 2 : Julia’s import is system specific and sometimes needs deep knowledge to debug the installation. It can also randomly stop functioning because of a dependecy update
  
- 3 : The way Julia packages are installed needs a long precompilation at each startup, which lower the interest of speeding the processes
  
- 4 : Embedding Julia in a python GUI is difficult and is not compatible with running multiple functions in parallel

Docker is explicitly made to counter those issues :
- 1 : The use of an image means that the installation is done only once (by the Docker image owner, which means me), and is transparent to the user
  
- 2 : Julia is contained in a fixed system, in our case a debian system, and its dependencies are therefore fixed and functioning. Which means no random upgrade can occur and no system specific debugging is needed
  
- 3 : SeaGap precompilation is already made at build, which means the user can directly run "using SeaGap" without any precompilation, at any time.
  
- 4 : With one image, you can create and parallelly run as many containers as you like. Meaning, you can manage parallel runs of multiple SeaGap functions without any multithreading issues.
