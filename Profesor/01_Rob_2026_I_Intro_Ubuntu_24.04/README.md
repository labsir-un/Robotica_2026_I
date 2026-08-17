<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>Introducción a Linux</h1>

<h2>Guía 01 - Instalación y Uso Básico de Ubuntu 24.04 LTS (Noble Numbat)</h2>

<h4><b>Base del curso:</b> Ubuntu 24.04 LTS + ROS 2 Jazzy Jalisco</h4>

<h5>Pedro Fabián Cárdenas Herrera<br>
    Manuel Felipe Carranza Montenegro</h5>

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
- [Recomendación del curso](#recomendación-del-curso)
- [Comparativa de distribuciones Linux para desarrollo y robótica](#comparativa-de-distribuciones-linux-para-desarrollo-y-robótica)
- [Métodos de instalación](#métodos-de-instalación)
- [Instrucciones de instalación según el método](#instrucciones-de-instalación-según-el-método)
  - [Instalación nativa](#instalación-nativa)
  - [Dual boot (Ubuntu + Windows)](#dual-boot-ubuntu--windows)
  - [Máquina virtual (VirtualBox / VMware)](#máquina-virtual-virtualbox--vmware)
  - [WSL2 (Windows Subsystem for Linux)](#wsl2-windows-subsystem-for-linux)
  - [Contenedores (Docker)](#contenedores-docker)
- [Primeros pasos después de instalar](#primeros-pasos-después-de-instalar)
- [Principales comandos de Ubuntu](#principales-comandos-de-ubuntu)
- [Bibliografía](#bibliografía)

---

## Introducción

En el desarrollo de sistemas de robótica moderna, inteligencia artificial y automatización, contar con un entorno operativo **estable, reproducible y compatible** con herramientas de software actuales es fundamental. Linux, con su ecosistema abierto y su fuerte adopción industrial y académica, se ha consolidado como el sistema operativo por excelencia en estos ámbitos.

Para el curso, se adopta **Ubuntu 24.04 LTS (Noble Numbat)** como estándar recomendado, junto con **ROS 2 Jazzy Jalisco**. Esta elección prioriza:

- **Soporte LTS** (mantenimiento de seguridad por 5 años, con posibilidad de extensión).
- **Compatibilidad oficial con ROS 2 Jazzy**, incluyendo paquetes `.deb` para Ubuntu 24.04.
- Un equilibrio entre **estabilidad**, **actualidad de librerías** y **facilidad de uso** para estudiantes.

> Nota: Ubuntu 24.04 LTS es una versión de soporte extendido (LTS). En cursos y laboratorios, esto reduce problemas por cambios frecuentes en versiones y dependencias.

---

## Objetivos

- **Presentar las principales opciones de instalación de Ubuntu 24.04 LTS**, comparando su funcionalidad, ventajas y limitaciones según el entorno de trabajo.
- **Comparar Ubuntu 24.04 con otras distribuciones Linux relevantes**, evaluando criterios como estabilidad, soporte, facilidad de uso y compatibilidad con ROS 2.
- **Justificar la elección de Ubuntu 24.04 LTS** como entorno recomendado para proyectos educativos, académicos o industriales relacionados con robótica y desarrollo de software.
- **Brindar una guía clara y práctica** para que el estudiante instale, prepare y verifique su entorno Linux sin fricción innecesaria.

---

## Recomendación del curso

✅ **Recomendado (ideal):** Instalación nativa o Dual Boot con **Ubuntu 24.04 LTS + ROS 2 Jazzy**  
⚠️ **Aceptable (con limitaciones):** Máquina virtual / WSL2 (según el caso de uso)  
🧪 **Avanzado (muy útil, pero requiere experiencia):** Docker/Contenedores

**¿Cuándo NO usar VM o WSL2?**  
- Cuando necesitas simulación pesada (Gazebo), gráficos 3D exigentes o GPU (sin configuración avanzada).
- Cuando trabajas con sensores/USB en tiempo real (LIDAR, cámaras, controladores).

---

## Comparativa de distribuciones Linux para desarrollo y robótica

> La compatibilidad con ROS 2 no depende solo del kernel: también depende de librerías, toolchains, versiones de Python, OpenSSL, y de si existen repos oficiales con binarios.

| Distribución | Estabilidad | ROS 2 (enfoque del curso) | Soporte comunidad | Facilidad de uso | Ciclo de soporte | ¿Por qué no se elige como base del curso? |
|---|---:|---|---|---:|---|---|
| **Ubuntu 24.04 LTS** | Alta | **Excelente (ROS 2 Jazzy con paquetes `.deb`)** | Enorme | Alta | **LTS (5 años+)** | — |
| Ubuntu 22.04 LTS | Alta | Buena (ideal para ROS 2 Humble; Jazzy suele ser desde fuente) | Enorme | Alta | LTS | Se estandariza en 24.04 para alinear el curso a Jazzy y toolchains más recientes. |
| Debian | Muy alta | Parcial (frecuente uso “desde fuente” / más ajustes) | Grande | Media | Muy largo | Más fricción para estudiantes: repos, dependencias y pasos extra. |
| Fedora | Media | Variable (cambios rápidos) | Media | Moderna | Corto | Actualizaciones frecuentes pueden romper dependencias o flujos de laboratorio. |
| Arch Linux | Variable | No recomendado para curso (rolling) | Técnica | Avanzado | Rolling | Alta probabilidad de “romperse” con actualizaciones; no es ideal para clases. |
| Rocky / RHEL | Alta | Parcial (enfocado enterprise) | Media | Media | Largo | Más orientado a servidores; curva adicional para entorno de escritorio. |
| Pop!_OS / Mint | Alta | Compatible (basado en Ubuntu) | Activa | Muy amigable | Medio/LTS | No es la referencia directa de ROS; puede variar en repos o toolchains. |

---

## Métodos de instalación

Antes de comenzar, define **tu método de instalación**. Lo más importante es balancear: rendimiento, facilidad y compatibilidad con lo que vas a usar en el curso.

| Método | Descripción | Ventajas | Desventajas |
|---|---|---|---|
| **Instalación nativa** | Ubuntu reemplaza el sistema actual. | Máximo rendimiento y estabilidad; acceso total al hardware. | Requiere backup; cambia por completo tu sistema. |
| **Dual Boot** | Ubuntu en partición aparte junto a Windows. | Rendimiento nativo; eliges sistema al arrancar. | Particionado; no se usan ambos sistemas simultáneamente. |
| **Máquina virtual (VM)** | Ubuntu dentro de Windows (VirtualBox/VMware). | Fácil de instalar/eliminar; ideal para aprender sin riesgo. | Rendimiento menor; gráficos/simuladores pueden ir lentos. |
| **WSL2** | Ubuntu dentro de Windows (sin VM “tradicional”). | Terminal potente; integración con Windows; ideal para desarrollo. | GUI/simuladores/sensores pueden requerir configuración adicional. |
| **Docker/Contenedores** | Ubuntu+ROS en contenedor (reproducible). | Portabilidad y entornos limpios; excelente para proyectos. | Curva de aprendizaje; acceso a dispositivos/GUI requiere configuración. |

---

## Instrucciones de instalación según el método

### Requisitos sugeridos (referencia rápida)

- **CPU:** 64-bit, 2 núcleos (mínimo) / 4+ recomendado  
- **RAM:** 4 GB (mínimo) / 8–16 GB recomendado (especialmente para simulación)  
- **Disco:** 25 GB (mínimo) / 60+ GB recomendado para ROS, simuladores y datasets  
- **Internet:** recomendado para actualizaciones y repositorios

---

### Instalación nativa

1. Descarga la ISO de **Ubuntu 24.04 LTS** desde el sitio oficial (releases).
2. Crea un USB booteable con **Rufus** (Windows) o **balenaEtcher** (Windows/macOS/Linux).
3. Reinicia y entra al BIOS/UEFI (`F2`, `F12`, `Del` o `Esc`) para arrancar desde el USB.
4. Selecciona **Install Ubuntu** y sigue el asistente.
5. En tipo de instalación, selecciona:
   - **Borrar disco e instalar Ubuntu** (solo si vas a reemplazar el sistema).
6. Configura usuario, contraseña y zona horaria.
7. Reinicia, retira el USB y verifica que entraste correctamente al sistema.

> Recomendación: si tu equipo tiene **Secure Boot**, Ubuntu suele funcionar bien. Si vas a instalar drivers propietarios (p.ej., NVIDIA), hazlo con cuidado y preferiblemente después de actualizar el sistema.

🎥 **Video sugerido (instalación paso a paso):**
- Búsqueda “Ubuntu 24.04 LTS install” (ver sección de *Videos recomendados* en [Bibliografía](#bibliografía)).

---

### Dual boot (Ubuntu + Windows)

1. En Windows, abre *Administración de discos* y reduce el volumen para dejar **25–60 GB** libres.
2. Crea un USB booteable con la ISO de Ubuntu 24.04 LTS.
3. Arranca desde el USB.
4. Selecciona **Install Ubuntu** → **Install alongside Windows** (si aparece).
5. Ajusta el tamaño de partición con el deslizador.
6. Finaliza instalación.
7. Al reiniciar, aparecerá **GRUB** para elegir entre Windows y Ubuntu.

> Sugerencia: si GRUB no aparece o hay problemas de arranque, revisa configuraciones UEFI/Legacy y el orden de booteo.

---

### Máquina virtual (VirtualBox / VMware)

**Recomendación de recursos (mínimo razonable):**
- 2–4 núcleos
- 4–8 GB RAM
- 50–80 GB disco virtual
- Acel. 3D activada (si el hipervisor lo permite)

#### Opción A — VirtualBox
1. Instala **VirtualBox 7.x**.
2. Crea una nueva VM (tipo Linux → Ubuntu 64-bit).
3. Asigna recursos y monta la ISO.
4. Inicia la VM y realiza la instalación normal de Ubuntu.
5. Instala **Guest Additions** para mejor resolución, portapapeles y carpetas compartidas.

> Tip: si Guest Additions falla, suele deberse a headers o herramientas de compilación faltantes (`build-essential`, `dkms`, `linux-headers-$(uname -r)`).

#### Opción B — VMware
1. Instala VMware Workstation/Player.
2. Crea una VM y monta la ISO de Ubuntu 24.04.
3. Instala Ubuntu y luego instala **VMware Tools** (mejora de drivers y experiencia gráfica).

🎥 **Videos del repositorio (si deseas mantenerlos):**
- Instalación VMware (general): https://github.com/user-attachments/assets/d33ad01a-0f71-42c8-a730-a9789a8949c6  
- Instalación Ubuntu (VMware) *(video previo puede seguir siendo útil, pero verifica que corresponda a 24.04)*: https://github.com/user-attachments/assets/8e603200-b8d1-4dae-872e-257750d92b8a  
- Instalación Ubuntu (VirtualBox) *(video previo puede seguir siendo útil, pero verifica que corresponda a 24.04)*: https://github.com/user-attachments/assets/8d22f098-0147-427b-837d-ce8a527d1816

---

### WSL2 (Windows Subsystem for Linux)

WSL2 es excelente si tu flujo es **desarrollo por terminal**, Git, Python y ROS sin depender de simuladores pesados.

1. Abre PowerShell como administrador y ejecuta:
   ```powershell
   wsl --install
   ```
2. Reinicia si Windows lo solicita.
3. Abre la app de Ubuntu (desde Microsoft Store o la instalación por defecto) y crea usuario/contraseña.
4. Verifica versiones e instalaciones:
   ```powershell
   wsl -l -v
   ```
5. Actualiza paquetes dentro de Ubuntu (WSL):
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

> Si necesitas GUI (RViz, etc.), Windows 11 incluye **WSLg**; aun así, para simulación exigente se recomienda instalación nativa/dual boot.

🎥 Video del repositorio:
- Instalación WSL2: https://github.com/user-attachments/assets/f3c41b45-3433-4dae-81b3-c95dded44e12

---

### Contenedores (Docker)

Docker es ideal para entornos **reproducibles** (mismos paquetes, misma versión de ROS, mismas dependencias).

1. Instala **Docker Desktop** (Windows/macOS) o Docker Engine (Linux).
2. En Windows, activa WSL2 como backend y habilita integración con tu distribución Ubuntu.
3. Descarga una imagen oficial de ROS 2 **Jazzy**:
   ```bash
   docker pull osrf/ros:jazzy-desktop
   ```
4. Ejecuta un contenedor interactivo:
   ```bash
   docker run -it osrf/ros:jazzy-desktop
   ```
5. (Opcional) Monta una carpeta local:
   ```bash
   docker run -it -v /ruta/local:/home/ros_user/workspace osrf/ros:jazzy-desktop
   ```

> Nota: para GUI (RViz/Gazebo) desde Docker necesitas configuración adicional (X11/Wayland o soluciones específicas según host).

---

## Primeros pasos después de instalar

### 1) Actualiza el sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl wget vim
```

### 2) Drivers y software adicional (recomendado)
- **Drivers adicionales:** *Software & Updates → Additional Drivers*
- **Codecs multimedia:**  
  ```bash
  sudo apt install -y ubuntu-restricted-extras
  ```

### 3) Herramientas de desarrollo útiles
```bash
sudo apt install -y python3-pip python3-venv
```

### 4) (Opcional) Preparación rápida para ROS 2 Jazzy
> En el curso se proveerán guías específicas de ROS 2, pero como verificación rápida puedes consultar la documentación oficial.

- Documentación oficial de instalación (Ubuntu 24.04): ver [Bibliografía](#bibliografía)

---

## Principales comandos de Ubuntu

| Comando | Función |
|---|---|
| `pwd` | Muestra la ruta del directorio actual. |
| `ls` | Lista los archivos y carpetas del directorio actual. |
| `cd nombre_directorio` | Cambia al directorio especificado. |
| `cd ..` | Sube un nivel. |
| `cd ~` | Va al directorio personal del usuario. |
| `mkdir nombre` | Crea una carpeta. |
| `rm nombre` | Elimina un archivo. |
| `rm -r carpeta` | Elimina una carpeta y su contenido. |
| `cp origen destino` | Copia archivos o carpetas. |
| `mv origen destino` | Mueve o renombra. |
| `touch archivo` | Crea un archivo vacío. |
| `nano archivo` | Editor de texto en terminal. |
| `cat archivo` | Muestra el contenido de un archivo. |
| `sudo comando` | Ejecuta como administrador. |
| `apt update` | Actualiza la lista de paquetes. |
| `apt upgrade` | Actualiza paquetes instalados. |
| `apt install paquete` | Instala un paquete. |
| `apt remove paquete` | Elimina un paquete. |
| `clear` | Limpia la terminal. |
| `history` | Historial de comandos. |
| `df -h` | Uso de disco en formato legible. |
| `top` | Procesos en ejecución. |
| `ps aux` | Lista procesos activos. |
| `kill PID` | Finaliza un proceso. |
| `chmod` | Cambia permisos. |
| `chown` | Cambia propietario. |
| `ping ip` | Verifica conectividad. |
| `ip a` | Información de red. |
| `tar -czvf file.tar.gz carpeta/` | Comprime en tar.gz. |
| `tar -xzvf file.tar.gz` | Descomprime tar.gz. |
| `man comando` | Manual de ayuda. |
| `exit` | Cierra la sesión/terminal. |

---

## Bibliografía

> Formato IEEE (enlaces incluidos para consulta rápida)

[1] Ubuntu Community Hub, “Ubuntu 24.04 LTS (Noble Numbat) Release Notes,” 2024.  
Disponible: https://discourse.ubuntu.com/t/ubuntu-24-04-lts-noble-numbat-release-notes/39890

[2] Ubuntu Releases, “Ubuntu 24.04 (Noble) Downloads,” 2024–2025.  
Disponible: https://releases.ubuntu.com/noble

[3] Canonical, “Ubuntu Desktop 24.04 LTS: Noble Numbat deep dive,” 2024.  
Disponible: https://ubuntu.com/blog/ubuntu-desktop-24-04-noble-numbat-deep-dive

[4] ROS 2 Documentation, “Jazzy: Installation,” 2024.  
Disponible: https://docs.ros.org/en/jazzy/Installation.html

[5] ROS 2 Documentation, “Ubuntu (deb packages) — Jazzy,” 2024.  
Disponible: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

[6] Open Robotics, “REP 2000 — ROS 2 Releases and Target Platforms,” 2024–2025.  
Disponible: https://www.ros.org/reps/rep-2000.html

[7] Microsoft Learn, “How to install Linux on Windows with WSL,” 2025.  
Disponible: https://learn.microsoft.com/en-us/windows/wsl/install

[8] Ubuntu Documentation, “Install Ubuntu on WSL 2,” 2024–2025.  
Disponible: https://documentation.ubuntu.com/wsl/stable/howto/install-ubuntu-wsl2/

[9] Docker Documentation, “Docker Desktop WSL 2 backend,” 2025.  
Disponible: https://docs.docker.com/desktop/features/wsl/

[10] Ubuntu Community Help Wiki, “Installation/SystemRequirements,” 2024.  
Disponible: https://help.ubuntu.com/community/Installation/SystemRequirements

[11] Oracle, “VirtualBox 7.0 User Manual,” 2024.  
Disponible: https://docs.oracle.com/en/virtualization/virtualbox/7.0/user/EN-VBOX-7-0-USER.pdf

### Videos recomendados (opcionales)
> Sugerencia: prioriza canales oficiales o educativos. Estos enlaces se proponen como apoyo visual.

- Instalación Ubuntu 24.04 (tutorial general): https://www.youtube.com/watch?v=WiW4KN2rNZY  
- Instalación ROS 2 Jazzy en Ubuntu 24.04 (tutorial general): https://www.youtube.com/watch?v=zaKCYGf6k08  
- Instalación WSL (documentación + video corto Microsoft): https://learn.microsoft.com/es-es/shows/one-dev-minute/how-do-i-install-wsl--one-dev-question

</div>
