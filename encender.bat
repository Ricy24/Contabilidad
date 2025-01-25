@echo off
REM Cambiar a la carpeta del proyecto
cd /d "C:\Users\LENOVO\Documents\las mairas"

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Cambiar al directorio del proyecto
cd restaurante_contabilidad

REM Iniciar el servidor de Django
start cmd /k "python manage.py runserver"

REM Abrir el navegador en la dirección del servidor
start http://127.0.0.1:8000

exit

