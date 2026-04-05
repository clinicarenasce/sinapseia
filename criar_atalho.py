import winreg, os 
import subprocess 
 
script = r"C:\Users\conta\app.py" 
icone = r"C:\Users\conta\transcritor.ico" 
desktop = r"C:\Users\conta\Desktop\Transcritor de Aulas.bat" 
python = r"C:\Users\conta\AppData\Local\Python\pythoncore-3.14-64\python.exe" 
 
with open(desktop, "w") as f: 
    f.write(f'@echo off\n"{python}" "{script}"\n') 
 
print("Atalho criado na Area de Trabalho!") 
