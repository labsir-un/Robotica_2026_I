<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>Introducción a ROS 2 Jazzy</h1>

<h2>Guía 02 - Instalación de ROS 2 Jazzy en Ubuntu 24.04</h2>

<h4>Pedro Fabián Cárdenas Herrera<br>
    Manuel Felipe Carranza Montenegro</h4>

<p>
  <img alt="Ubuntu 24.04 LTS" src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420?logo=ubuntu&logoColor=white">
  <img alt="ROS 2 Jazzy" src="https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros&logoColor=white">
  <img alt="Nivel" src="https://img.shields.io/badge/Nivel-Introductorio-2ea44f">
</p>

</div>

<div align="justify"> 

## Tabla de contenidos
- [Introducción](#introducción)
- [Objetivos](#objetivos)
- [Requisitos previos](#requisitos-previos)
- [Instalación de herramientas previas](#instalación-de-herramientas-previas)
  - [1. Visual Studio Code](#1-visual-studio-code)
  - [2. Terminator](#2-terminator-terminal-recomendado)
- [Instalación de ROS 2 Jazzy](#instalación-de-ros-2-jazzy)
  - [0. Recomendación antes de empezar](#0-recomendación-antes-de-empezar-si-tenías-otra-versión-de-ros)
  - [1. Configuración del Locale (UTF-8)](#1-configuración-del-locale-utf-8)
  - [2. Configurar fuentes oficiales de ROS 2 Jazzy](#2-configurar-fuentes-oficiales-de-ros-2-jazzy)
  - [3. Instalación de ROS 2 Jazzy](#3-instalación-de-ros-2-jazzy)
- [Configuración del entorno](#configuración-del-entorno)
- [Herramientas de desarrollo recomendadas](#herramientas-de-desarrollo-recomendadas-para-el-curso)
  - [1. rosdep](#1-rosdep-resolver-dependencias)
  - [2. colcon](#2-colcon-compilación-de-workspaces)
- [Probar ROS 2 (talker-listener)](#probar-ros-2-ejemplo-talker-listener)
- [Workspace inicial (opcional)](#opcional-primera-estructura-de-workspace-colcon)
- [Solución de problemas comunes](#solución-de-problemas-comunes)
- [Recursos útiles](#recursos-útiles-para-seguir-aprendiendo)
- [Referencias](#referencias)

---

## Introducción

ROS 2 (Robot Operating System) es una infraestructura de software modular y abierta diseñada para el desarrollo de aplicaciones robóticas. Esta guía está dirigida a estudiantes y docentes de la Universidad Nacional de Colombia, especialmente aquellos vinculados a cursos de robótica, que deseen configurar un entorno de desarrollo con **ROS 2 Jazzy Jalisco (LTS)** sobre **Ubuntu 24.04 LTS (Noble Numbat)**.

Aquí se detallan paso a paso los comandos necesarios para instalar ROS 2, configurar el entorno, instalar herramientas útiles como Visual Studio Code y Terminator, y realizar una primera prueba con nodos de ejemplo (talker y listener).

## Objetivos

- Proporcionar una guía clara y funcional para instalar ROS 2 Jazzy sobre Ubuntu 24.04.
- Asegurar que el entorno de desarrollo esté correctamente configurado para trabajar con ROS 2.
- Introducir herramientas útiles como Terminator y Visual Studio Code para facilitar el desarrollo y la organización del trabajo.
- Verificar la instalación de ROS 2 mediante la ejecución de nodos de ejemplo (talker y listener).
- Dejar listo el entorno base para compilar paquetes con `colcon` y resolver dependencias con `rosdep`.

---

## Requisitos previos

- Tener instalado **Ubuntu 24.04 LTS (Noble Numbat)** (idealmente instalación nativa o dual boot).
- Conexión a internet estable.
- Usuario con permisos `sudo`.
- Recomendado: sistema actualizado antes de iniciar.

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Instalación de herramientas previas

### 1. Visual Studio Code

Visual Studio Code es un editor de código moderno, ligero y con extensiones útiles para C++, Python y ROS.

> Nota: Este método instala VS Code desde el repositorio oficial de Microsoft para recibir actualizaciones por `apt`.

```bash
sudo apt update
sudo apt install wget gpg -y

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /usr/share/keyrings/
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] \
https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'

sudo apt update
sudo apt install code -y
```

### 2. Terminator (Terminal recomendado)

Terminator permite dividir la terminal en múltiples paneles. Es muy útil para ejecutar varios nodos o comandos ROS simultáneamente.

```bash
sudo apt update
sudo apt install terminator -y
```

---

## Instalación de ROS 2 Jazzy

### 0. Recomendación antes de empezar (si tenías otra versión de ROS)

Si tenías ROS 2 instalado previamente (ej. Humble), evita mezclar entornos. En un curso, lo más estable es trabajar con **una sola distribución** por instalación de Ubuntu.

Verifica qué tienes instalado:
```bash
dpkg -l | grep ros- | head
```

---

### 1. Configuración del Locale (UTF-8)

ROS 2 necesita un entorno con soporte para UTF-8. Este paso garantiza compatibilidad con herramientas y mensajes.

```bash
locale  # Verifica si ya tienes UTF-8 habilitado

sudo apt update
sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # Verifica que los cambios se hayan aplicado
```

---

### 2. Configurar fuentes oficiales de ROS 2 Jazzy

ROS 2 no viene en los repositorios por defecto, así que hay que agregar sus fuentes oficiales.

#### 2.1 Habilitar repositorio Universe

```bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository universe
```

#### 2.2 Agregar la clave GPG de ROS 2

```bash
sudo apt update
sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
-o /usr/share/keyrings/ros-archive-keyring.gpg
```

#### 2.3 Agregar el repositorio de ROS 2

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
| sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

---

### 3. Instalación de ROS 2 Jazzy

1) Actualiza paquetes del sistema:

```bash
sudo apt update
sudo apt upgrade -y
```

2) Instala ROS 2 Jazzy:

#### Opción A: Versión completa (recomendada para GUI y RViz)
```bash
sudo apt install ros-jazzy-desktop -y
```

#### Opción B: Versión base (más ligera, sin GUI pesada)
```bash
sudo apt install ros-jazzy-ros-base -y
```

---

## Configuración del entorno

### 1) Activar ROS 2 en la sesión actual

```bash
source /opt/ros/jazzy/setup.bash
```

### 2) Activar ROS 2 automáticamente al abrir una terminal (recomendado)

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

> Nota: Si usas `zsh`, reemplaza `~/.bashrc` por `~/.zshrc`.

---

## Herramientas de desarrollo recomendadas (para el curso)

### 1. rosdep (resolver dependencias)

```bash
sudo apt install python3-rosdep -y
sudo rosdep init
rosdep update
```

### 2. colcon (compilación de workspaces)

```bash
sudo apt install python3-colcon-common-extensions python3-argcomplete -y
```

Verificación rápida:
```bash
colcon --help
```

---

## Probar ROS 2 (Ejemplo talker-listener)

Esta prueba lanza un nodo emisor y un nodo receptor.

1) En una terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_cpp talker
```

2) En otra terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_py listener
```

Si todo está correcto, verás que el listener recibe mensajes del talker.

---

## (Opcional) Primera estructura de workspace (colcon)

```bash
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Para instalar dependencias cuando tengas paquetes en `src/`:

```bash
cd ~/colcon_ws
rosdep install --from-paths src --ignore-src -r -y
```

---

## Solución de problemas comunes

### 1) `ros2: command not found`
- Asegúrate de haber ejecutado:
  ```bash
  source /opt/ros/jazzy/setup.bash
  ```
- Verifica que exista la carpeta:
  ```bash
  ls /opt/ros/
  ```

### 2) Errores al agregar repositorio o llave GPG
- Repite el paso de la llave GPG y el repo, y luego:
  ```bash
  sudo apt update
  ```

### 3) `rosdep init` falla por permisos o archivo existente
- Si ya estaba inicializado, solo ejecuta:
  ```bash
  rosdep update
  ```

---

## Recursos útiles (para seguir aprendiendo)

- Documentación oficial de ROS 2 Jazzy (instalación y tutoriales).
- Índice de instalación de ROS 2 Jazzy (opciones y plataformas).
- Guías de ROS 2 para Docker (si trabajas con contenedores).
- Documentación oficial de VS Code en Linux.

---

## Referencias

1. ROS 2 Jazzy — Installation (índice): https://docs.ros.org/en/jazzy/Installation.html  
2. ROS 2 Jazzy — Ubuntu (Deb packages): https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html  
3. Open Robotics — ROS Jazzy Jalisco released: https://www.openrobotics.org/blog/2024/5/ros-jazzy-jalisco-released  
4. Visual Studio Code — Setup en Linux: https://code.visualstudio.com/docs/setup/linux  
5. ROS 2 Jazzy — Run nodes in Docker: https://docs.ros.org/en/jazzy/How-To-Guides/Run-2-nodes-in-single-or-separate-docker-containers.html  
6. Docker Hub — osrf/ros tags: https://hub.docker.com/r/osrf/ros/tags  

</div>
