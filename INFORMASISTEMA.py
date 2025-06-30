import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import psutil
import platform
import os
import json
import csv
from datetime import datetime
import requests 

def get_system_info():
    """
    Obtiene la información del sistema utilizando psutil, platform y os.
    """
    info = {}

    # Información del CPU
    info['CPU Info'] = {
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        # Usamos interval=0.1 para una lectura más rápida sin retrasos
        "Current frequency (Mhz)": f"{psutil.cpu_freq().current:.2f}",
        "Total CPU usage (%)": f"{psutil.cpu_percent(interval=0.5):.2f}"
    }

    # Procesos corriendo
    info['Running Processes'] = len(psutil.pids())

    # Usuario que tiene la sesión abierta
    try:
        users = psutil.users()
        if users:
            info['Logged in User'] = users[0].name
        else:
            info['Logged in User'] = "N/A"
    except Exception:
        info['Logged in User'] = "N/A"

    # Nombre y versión del sistema operativo
    info['Operating System'] = {
        "Name": platform.system(),
        "Version": platform.version(),
        "Release": platform.release(),
        "Architecture": platform.machine()
    }
    
    return info

def update_info_display(text_widget):
    """
    Actualiza la información mostrada en el widget de texto.
    """
    info = get_system_info()
    text_widget.config(state=tk.NORMAL)
    text_widget.delete('1.0', tk.END)
    
    text_widget.insert(tk.END, "--- Información del CPU ---\n")
    for key, value in info['CPU Info'].items():
        text_widget.insert(tk.END, f"{key}: {value}\n")
    
    text_widget.insert(tk.END, "\n--- Procesos en Ejecución ---\n")
    text_widget.insert(tk.END, f"Total de procesos: {info['Running Processes']}\n")
    
    text_widget.insert(tk.END, "\n--- Usuario con Sesión Activa ---\n")
    text_widget.insert(tk.END, f"Usuario: {info['Logged in User']}\n")
    
    text_widget.insert(tk.END, "\n--- Información del Sistema Operativo ---\n")
    for key, value in info['Operating System'].items():
        text_widget.insert(tk.END, f"{key}: {value}\n")
    
    text_widget.config(state=tk.DISABLED)

def update_info_display_auto(text_widget, root):
    """
    Actualiza la información en la pantalla y programa la próxima actualización.
    """
    update_info_display(text_widget)
    
    root.after(1000, update_info_display_auto, text_widget, root)

def save_to_json(info_data, file_path):
    """
    Guarda los datos del sistema en un archivo JSON.
    """
    ordered_json_info = {
        "CPU Info": info_data.get("CPU Info", {}),
        "Running Processes": info_data.get("Running Processes", 0),
        "Logged in User": info_data.get("Logged in User", "N/A"),
        "Operating System": info_data.get("Operating System", {})
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_json_info, f, indent=4, ensure_ascii=False)

def save_to_csv(info_data, file_path):
    """
    Guarda los datos del sistema en un archivo CSV estructurado como una tabla horizontal,
    con los encabezados de las propiedades en la primera fila y los valores en la segunda.
    """
    
    headers = [
        "CPUs Fisicos",
        "Nucleos Logicos CPU",
        "Frecuencia Actual CPU (MHz)",
        "Uso Total CPU (%)",
        "Total Procesos en Ejecucion",
        "Usuario de Sesion",
        "Nombre Sistema Operativo",
        "Version SO",
        "Release Sistema Operativo",
        "Arquitectura Sistema Operativo"
    ]
    
   
    data_mapping = {
        "CPUs Fisicos": info_data['CPU Info'].get("Physical cores", ""),
        "Nucleos Logicos CPU": info_data['CPU Info'].get("Total cores", ""),
        "Frecuencia Actual CPU (MHz)": info_data['CPU Info'].get("Current frequency (Mhz)", ""),
        "Uso Total CPU (%)": info_data['CPU Info'].get("Total CPU usage (%)", ""),
        "Total Procesos en Ejecucion": info_data.get("Running Processes", ""),
        "Usuario de Sesion": info_data.get("Logged in User", ""),
        "Nombre Sistema Operativo": info_data['Operating System'].get("Name", ""),
        "Version SO": info_data['Operating System'].get("Version", ""),
        "Release Sistema Operativo": info_data['Operating System'].get("Release", ""),
        "Arquitectura Sistema Operativo": info_data['Operating System'].get("Architecture", "")
    }

   
    data_row = [data_mapping[header] for header in headers]
    
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow(headers)
        
        writer.writerow(data_row)

def save_all_files():
    """
    Maneja el diálogo de guardado y llama a las funciones para guardar
    los archivos JSON y CSV.
    """
    info = get_system_info()

    try:
        base_file_path = filedialog.asksaveasfilename(
            defaultextension="",
            filetypes=[("All files", "*.*")],
            initialfile=f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not base_file_path:
            return

        json_file_path = f"{base_file_path}.json"
        csv_file_path = f"{base_file_path}.csv"

        save_to_json(info, json_file_path)
        save_to_csv(info, csv_file_path)
            
        messagebox.showinfo("Guardado Exitoso", 
                            f"Datos guardados en:\n{os.path.basename(json_file_path)}\n{os.path.basename(csv_file_path)}")
        
    except Exception as e:
        messagebox.showerror("Error al Guardar", f"No se pudieron guardar los archivos: {e}")
        
def send_data_to_api():
    """
    Obtiene la información del sistema y la envía a un endpoint de API.
    """
    
    api_url = "http://127.0.0.1:5000/recolectar" 
    
    info = get_system_info()
    
    try:
        
        response = requests.post(api_url, json=info)
        
       
        if response.status_code == 201:
            messagebox.showinfo("Envío Exitoso", f"Datos enviados correctamente a la API: {api_url}")
        else:
            messagebox.showerror("Error de Envío", 
                                 f"Fallo al enviar datos. Código de estado: {response.status_code}\n"
                                 f"Respuesta del servidor: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la API en {api_url}:\n{e}")




def create_gui():
    """
    Crea la interfaz gráfica con Tkinter y un diseño moderno.
    """
    root = tk.Tk()
    root.title("Información del Sistema")
    root.geometry("600x700")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('clam')

    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 15))
    style.configure("TButton", font=("Segoe UI", 15, "bold"), padding=8)
    style.map("TButton", background=[('active', '#e0e0e0')])

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_label = ttk.Label(main_frame, text="Detalles del Sistema", font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=(0, 15))

    info_text = tk.Text(main_frame, wrap=tk.WORD, font=("Segoe UI", 12), 
                        bg="#ffffff", fg="#333333", relief=tk.FLAT, bd=0, padx=10, pady=10)
    info_text.pack(fill=tk.BOTH, expand=True)
    info_text.config(state=tk.DISABLED)

    button_frame = ttk.Frame(main_frame, padding="10")
    button_frame.pack(fill=tk.X, pady=(15, 0))
    
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1) 

    save_all_button = ttk.Button(button_frame, text="Guardar JSON y CSV", command=save_all_files)
    save_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    
    send_api_button = ttk.Button(button_frame, text="Enviar a API", command=send_data_to_api)
    send_api_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    exit_button = ttk.Button(button_frame, text="Salir", command=root.quit, style="TButton")
    exit_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    
    update_info_display_auto(info_text, root)

    root.mainloop()

if __name__ == "__main__":
    create_gui()