import requests
import time
import random
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from datetime import datetime
import os
import logging

class DiscordMessageDeleter:
    CONFIG_FILE = "config.json"
    LOG_FILE = "delete_log.txt"
    VERSION = "1.0"
    
    def __init__(self):
        self.running = False
        self.deleted_count = 0
        self.total_messages = 0
        self.setup_logging()
        self.create_gui()
        
    def setup_logging(self):
        """Configura el sistema de logging para archivo y consola"""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(self.LOG_FILE, 'a', 'utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def create_gui(self):
        """Crea la interfaz gráfica mejorada"""
        self.root = tk.Tk()
        self.root.title(f"Discord Message Deleter by bloodyzeze. v{self.VERSION}")
        self.root.geometry("600x500")
        self.root.configure(bg="#36393f")
        
        # Aplicar estilo Discord-like
        self.setup_styles()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#36393f", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de configuración
        self.create_config_area(main_frame)
        
        # Área de opciones
        self.create_options_area(main_frame)
        
        # Botones de acción
        self.create_buttons_area(main_frame)
        
        # Área de logs
        self.create_logs_area(main_frame)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para comenzar")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cargar token guardado
        self.load_saved_config()
        
        # Iniciar la GUI
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def setup_styles(self):
        """Configura los estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos para botones y etiquetas
        style.configure('TButton', font=('Arial', 11), background='#5865f2', foreground='white')
        style.configure('TLabel', font=('Arial', 11), background='#36393f', foreground='white')
        style.configure('TEntry', font=('Arial', 11))
        style.map('TButton', background=[('active', '#4752c4')])
        
    def create_config_area(self, parent):
        """Crea el área de configuración principal"""
        # Token de Discord
        ttk.Label(parent, text="Token de Discord:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.entry_token = ttk.Entry(parent, width=70)
        self.entry_token.pack(fill=tk.X, pady=(0, 10))
        
        # ID del Canal
        ttk.Label(parent, text="ID del Canal (DM/Grupo/Servidor):", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.entry_channel_id = ttk.Entry(parent, width=70)
        self.entry_channel_id.pack(fill=tk.X, pady=(0, 10))
    
    def create_options_area(self, parent):
        """Crea el área de opciones adicionales"""
        options_frame = tk.Frame(parent, bg="#36393f")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Limitar número de mensajes
        ttk.Label(options_frame, text="Límite de mensajes (0 = sin límite):", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.entry_limit = ttk.Entry(options_frame, width=10)
        self.entry_limit.grid(row=0, column=1, sticky=tk.W)
        self.entry_limit.insert(0, "0")
        
        # Retraso entre borrados
        ttk.Label(options_frame, text="Retraso (seg):", style='TLabel').grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.entry_delay = ttk.Entry(options_frame, width=5)
        self.entry_delay.grid(row=0, column=3, sticky=tk.W)
        self.entry_delay.insert(0, "0.5")
    
    def create_buttons_area(self, parent):
        """Crea el área de botones de acción"""
        buttons_frame = tk.Frame(parent, bg="#36393f")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(buttons_frame, text="▶️ Iniciar Borrado", command=self.start_deletion)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = ttk.Button(buttons_frame, text="⏹️ Detener", command=self.stop_deletion, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🔄 Limpiar Logs", command=self.clear_logs).pack(side=tk.LEFT)
    
    def create_logs_area(self, parent):
        """Crea el área de logs"""
        log_frame = tk.LabelFrame(parent, text="Logs", bg="#2f3136", fg="white", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.text_logs = scrolledtext.ScrolledText(log_frame, width=70, height=15, bg="#2f3136", fg="#dcddde", font=("Consolas", 9))
        self.text_logs.pack(fill=tk.BOTH, expand=True)
    
    def load_saved_config(self):
        """Carga la configuración guardada"""
        token = self.load_config()
        if token:
            self.entry_token.insert(0, token)
            self.log("✅ Token cargado desde configuración")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.running:
            if not messagebox.askyesno("Confirmar salida", "Hay un proceso de borrado en curso. ¿Realmente deseas salir?"):
                return
            self.stop_deletion()
        self.root.destroy()
    
    def load_config(self):
        """Carga el token desde el archivo de configuración"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("token", "")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return ""
    
    def save_config(self, token):
        """Guarda el token en el archivo de configuración"""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump({"token": token}, f, indent=4)
            self.log("✅ Token guardado en configuración")
        except Exception as e:
            self.log(f"❌ Error al guardar configuración: {str(e)}")
    
    def log(self, message):
        """Registra mensajes en la interfaz y archivo de log"""
        # Registrar en el sistema de logging
        logging.info(message)
        
        # Mostrar en la GUI
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_logs.insert(tk.END, f"[{timestamp}] {message}\n")
        self.text_logs.yview(tk.END)
    
    def clear_logs(self):
        """Limpia el área de logs"""
        self.text_logs.delete(1.0, tk.END)
        self.log("🧹 Logs limpiados")
    
    def update_status(self, message):
        """Actualiza la barra de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def get_user_id(self, token):
        """Obtiene el ID del usuario a partir del token"""
        url = "https://discord.com/api/v9/users/@me"
        headers = self._get_headers(token)
        
        try:
            response = self._make_request("get", url, headers=headers)
            if response and response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username', 'Unknown')
                discrim = user_data.get('discriminator', '0000')
                self.log(f"👤 Usuario identificado: {username}#{discrim}")
                return user_data["id"]
            else:
                status = response.status_code if response else "Error de conexión"
                self.log(f"❌ Error al obtener ID de usuario: {status}")
                return None
        except Exception as e:
            self.log(f"❌ Error de conexión: {str(e)}")
            return None
    
    def get_messages(self, token, channel_id, user_id, limit=0):
        """Obtiene los mensajes del canal de manera eficiente"""
        headers = self._get_headers(token)
        messages = []
        
        max_messages = 5000 if limit <= 0 else min(limit, 5000)
        
        self.log(f"🔍 Buscando mensajes en el canal {channel_id}...")
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"
        
        while len(messages) < max_messages and self.running:
            try:
                response = self._make_request("get", url, headers=headers)
                
                if not response or response.status_code != 200:
                    status = response.status_code if response else "Error de conexión"
                    self.log(f"❌ Error al obtener mensajes: {status}")
                    break
                
                batch = response.json()
                if not batch:
                    break  # No hay más mensajes
                
                # Filtrar solo los mensajes del usuario
                user_messages = [m for m in batch if m['author']['id'] == user_id]
                messages.extend(user_messages)
                
                self.update_status(f"Encontrados {len(messages)} mensajes...")
                
                # Si ya alcanzamos el límite
                if limit > 0 and len(messages) >= limit:
                    messages = messages[:limit]
                    break
                
                # Verificar si quedan más mensajes
                if len(batch) < 100:
                    break
                
                # Construir URL para el siguiente lote
                url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100&before={batch[-1]['id']}"
                
                # Delay adaptativo
                time.sleep(random.uniform(0.5, 0.8))
                
            except Exception as e:
                self.log(f"❌ Error al procesar mensajes: {str(e)}")
                time.sleep(2)  # Esperar antes de reintentar
                
        self.log(f"✅ Se encontraron {len(messages)} mensajes para eliminar")
        return messages
    
    def delete_message(self, token, channel_id, message):
        """Borra un mensaje de manera segura"""
        if not self.running:
            return False
            
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message['id']}"
        headers = self._get_headers(token)
        
        max_attempts = 5
        backoff_time = 1
        
        for attempt in range(max_attempts):
            if not self.running:
                return False
                
            response = self._make_request("delete", url, headers=headers)
            
            if not response:
                time.sleep(2 + attempt)
                continue
                
            if response.status_code == 204:
                # Mensaje truncado si es muy largo
                content = message.get('content', '')
                if len(content) > 50:
                    content = content[:47] + "..."
                
                # Añadir verificación para mensajes con archivos adjuntos
                if message.get('attachments') and len(message['attachments']) > 0:
                    content += f" [+{len(message['attachments'])} adjuntos]"
                
                self.log(f"✅ Eliminado: ID={message['id']} | '{content}'")
                return True
                
            elif response.status_code == 429:  # Rate limit
                retry_time = self._handle_rate_limit(response, attempt)
                time.sleep(retry_time)
                
            elif response.status_code in (403, 404):
                # Mensaje ya borrado o sin permiso
                return False
                
            else:
                # Otros errores
                self.log(f"⚠️ Error {response.status_code} al borrar mensaje {message['id']}")
                wait_time = backoff_time * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(min(wait_time, 30))
        
        return False
    
    def _handle_rate_limit(self, response, attempt=0):
        """Maneja los rate limits de la API de Discord"""
        try:
            data = response.json()
            retry_after = float(data.get('retry_after', response.headers.get('Retry-After', 5)))
        except:
            retry_after = 5 + attempt
            
        self.log(f"⚠️ Rate limit alcanzado. Esperando {retry_after:.2f} segundos...")
        return retry_after + 0.5
    
    def _get_headers(self, token):
        """Retorna los headers necesarios para las peticiones a Discord"""
        return {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVzLUVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzkxLjAuNDQ3Mi4xMjQgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjkxLjAuNDQ3Mi4xMjQiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTM3MTYsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me"
        }
    
    def _make_request(self, method, url, headers=None, data=None, json_data=None):
        """Método centralizado para realizar peticiones HTTP con manejo de errores"""
        try:
            if method.lower() == "get":
                return requests.get(url, headers=headers)
            elif method.lower() == "post":
                return requests.post(url, headers=headers, data=data, json=json_data)
            elif method.lower() == "delete":
                return requests.delete(url, headers=headers)
            else:
                return None
        except requests.exceptions.ConnectionError:
            self.log(f"⚠️ Error de conexión al hacer petición a {url}")
            return None
        except Exception as e:
            self.log(f"❌ Error en solicitud HTTP: {str(e)}")
            return None
    
    def deletion_worker(self, token, channel_id, user_id, delay, limit):
        """Proceso principal de borrado optimizado y seguro"""
        try:
            self.log("🔄 Iniciando proceso de búsqueda de mensajes...")
            
            # Obtener mensajes
            messages = self.get_messages(token, channel_id, user_id, limit)
            
            if not messages or not self.running:
                self.log("ℹ️ No se encontraron mensajes para eliminar o proceso detenido")
                self.finalize_deletion()
                return
            
            self.total_messages = len(messages)
            self.deleted_count = 0
            failures = 0
            consecutive_failures = 0
            last_success_time = time.time()
            
            # Ordenar mensajes: primero los más recientes para reducir problemas
            messages.sort(key=lambda x: int(x['id']), reverse=True)
            
            self.log(f"🗑️ Comenzando eliminación de {self.total_messages} mensajes...")
            
            for idx, msg in enumerate(messages):
                if not self.running:
                    self.log("🛑 Proceso de borrado detenido por el usuario")
                    break
                
                # Verificar si llevamos mucho tiempo sin éxito
                if self._should_pause_for_errors(consecutive_failures, last_success_time):
                    self.log("⚠️ Demasiados errores consecutivos. Pausando 30 segundos...")
                    time.sleep(30)
                    consecutive_failures = 0
                
                # Borrar el mensaje
                success = self.delete_message(token, channel_id, msg)
                
                if success:
                    self.deleted_count += 1
                    consecutive_failures = 0
                    last_success_time = time.time()
                    
                    # Ajustar delay adaptativo basado en éxito
                    if self.deleted_count % 10 == 0 and delay > 0.5:
                        delay = max(0.5, delay * 0.9)
                else:
                    failures += 1
                    consecutive_failures += 1
                    
                    # Aumentar delay si hay fallos
                    if consecutive_failures > 3:
                        delay = min(5.0, delay * 1.5)
                
                # Actualizar progreso
                self._update_progress(failures)
                
                # Actualizar UI cada 10 mensajes
                if idx % 10 == 0:
                    self.root.update_idletasks()
                
                # Esperar entre borrados con delay adaptativo
                if idx < len(messages) - 1 and self.running:
                    actual_delay = float(delay) + random.uniform(-0.1, 0.2)
                    time.sleep(max(0.3, actual_delay))
            
            # Mostrar resumen final
            if self.running:
                remaining = self.total_messages - self.deleted_count
                if remaining > 0 and self.deleted_count > 0:
                    self.log(f"🔄 Verificando mensajes restantes ({remaining})...")
            
            if self.deleted_count == self.total_messages and self.running:
                self.log(f"🎉 ¡Completado! Se eliminaron {self.deleted_count} mensajes")
            else:
                self.log(f"ℹ️ Proceso finalizado. Eliminados {self.deleted_count} de {self.total_messages} mensajes. Fallos: {failures}")
                
        except Exception as e:
            self.log(f"❌ Error en el proceso de borrado: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        
        self.finalize_deletion()
    
    def _should_pause_for_errors(self, consecutive_failures, last_success_time):
        """Determina si se debe pausar debido a errores consecutivos"""
        return (consecutive_failures > 10 or 
                (consecutive_failures > 5 and time.time() - last_success_time > 60))
    
    def _update_progress(self, failures):
        """Actualiza la información de progreso en la UI"""
        progress_pct = int(self.deleted_count/self.total_messages*100) if self.total_messages > 0 else 0
        self.update_status(f"Progreso: {self.deleted_count}/{self.total_messages} eliminados ({progress_pct}%) - Fallos: {failures}")
    
    def start_deletion(self):
        """Inicia el proceso de borrado"""
        token = self.entry_token.get().strip()
        channel_id = self.entry_channel_id.get().strip()
        
        # Validar campos
        if not token or not channel_id:
            messagebox.showerror("Error", "Debes ingresar tanto el token como la ID del canal")
            return
        
        # Obtener otros parámetros
        try:
            limit = int(self.entry_limit.get().strip() or "0")
            delay = float(self.entry_delay.get().strip() or "0.5")
            if delay < 0.1:
                delay = 0.1  # Mínimo retraso para evitar rate limits
        except ValueError:
            messagebox.showerror("Error", "Los valores de límite y retraso deben ser números")
            return
        
        # Guardar el token para futuro uso
        self.save_config(token)
        
        # Obtener ID de usuario
        user_id = self.get_user_id(token)
        if not user_id:
            messagebox.showerror("Error", "No se pudo obtener tu ID de usuario. Verifica tu token.")
            return
        
        # Iniciar el proceso
        self.running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Crear un hilo para el proceso
        threading.Thread(
            target=self.deletion_worker, 
            args=(token, channel_id, user_id, delay, limit),
            daemon=True
        ).start()
        
        self.log(f"▶️ Iniciando proceso de borrado (Límite: {'Sin límite' if limit <= 0 else limit}, Retraso: {delay}s)")
    
    def stop_deletion(self):
        """Detiene el proceso de borrado"""
        self.running = False
        self.btn_stop.config(state=tk.DISABLED)
        self.update_status("Deteniendo proceso...")
        self.log("⏸️ Deteniendo el proceso de borrado...")
    
    def finalize_deletion(self):
        """Finaliza el proceso y restaura la interfaz"""
        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.update_status("Listo")

# Iniciar la aplicación
if __name__ == "__main__":
    DiscordMessageDeleter()