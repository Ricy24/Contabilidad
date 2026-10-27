# 🧾 Contabilidad para Restaurantes

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

> Sistema de **contabilidad** para restaurantes y negocios: inventario, ventas y reportes, construido en Django.

---

## 📋 Descripción

Aplicación de escritorio/web para llevar la contabilidad de un restaurante o negocio: control de **inventario**, registro de **ventas** y generación de reportes, con una interfaz sencilla y base de datos propia.

## ✨ Características

- 📦 Gestión de **inventario**
- 💰 Registro y consulta de **ventas**
- 📊 Reportes y análisis de movimientos
- 👥 Gestión de usuarios
- 🗄️ Base de datos integrada (`db.sqlite3`)
- 🖥️ Plantillas HTML con Django Templates

## 🛠️ Stack

`Python` · `Django` · `SQLite` · `HTML/CSS`

## 🚀 Instalación

### Requisitos

- **Python 3.10+**

### Pasos

```bash
git clone https://github.com/Ricy24/Contabilidad.git
cd Contabilidad

python -m venv venv
venv\Scripts\activate

pip install django
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

> 💡 En Windows también puedes usar el accesore directo [`encender.bat`](encender.bat) para arrancar el servidor.

## 📁 Estructura

```text
Contabilidad/
├── restaurante_contabilidad/   # Proyecto Django (settings, urls)
├── main/                       # App principal
├── ventas/                     # Módulo de ventas
├── inventario/                 # Módulo de inventario
├── analisis/                   # Reportes y análisis
├── templates/                  # Plantillas HTML
├── media/                      # Archivos subidos
├── db.sqlite3                  # Base de datos
├── manage.py
└── encender.bat                # Arranque rápido (Windows)
```

## 📄 Licencia

Proyecto desarrollado con **fines académicos**.
