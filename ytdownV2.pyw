import customtkinter as ctk
import yt_dlp
import os
import threading
from tkinter import messagebox, filedialog

# Configuração Visual (Tema Dark Moderno)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QuartetoDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Janela
        self.title("Youtube Audio Downloader")
        self.geometry("650x480")

        # Layout Centralizado
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.label = ctk.CTkLabel(self, text="🎵 Youtube Downloader", font=("Roboto", 26, "bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(30, 10))

        # Campo de URL
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Cole o link do YouTube (Vídeo ou Playlist)...", 
                                      width=500, height=45)
        self.url_entry.grid(row=1, column=0, padx=20, pady=10)

        # Status e Info
        self.status_info = ctk.CTkLabel(self, text="Formato: MP3 | Taxa: 128 kbps", text_color="gray70")
        self.status_info.grid(row=2, column=0, padx=20, pady=5)

        # Tipo de Conteúdo e Resolução
        self.content_type = ctk.StringVar(value="audio")
        self.video_resolution = ctk.StringVar(value="720p")

        self.option_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.option_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.option_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.audio_radio = ctk.CTkRadioButton(self.option_frame, text="Áudio", variable=self.content_type, value="audio", command=self.on_type_change)
        self.audio_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.video_radio = ctk.CTkRadioButton(self.option_frame, text="Vídeo", variable=self.content_type, value="video", command=self.on_type_change)
        self.video_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.resolution_label = ctk.CTkLabel(self.option_frame, text="Resolução de vídeo:")
        self.resolution_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.resolution_menu = ctk.CTkOptionMenu(self.option_frame, values=["1080p", "720p", "480p", "360p"], variable=self.video_resolution, command=self.update_status_info)
        self.resolution_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.update_resolution_state()

        # Botão de Download
        self.download_button = ctk.CTkButton(self, text="SELECIONAR PASTA E BAIXAR", command=self.start_download_thread, 
                                             font=("Roboto", 16, "bold"), height=50, 
                                             fg_color="#1f538d", hover_color="#14375e")
        self.download_button.grid(row=4, column=0, padx=20, pady=20)

        # Console de Log
        self.textbox = ctk.CTkTextbox(self, width=550, height=150, font=("Consolas", 12))
        self.textbox.grid(row=5, column=0, padx=20, pady=10)
        self.log("Sistema Pronto. O ffmpeg deve estar na pasta do script.")

    def log(self, text):
        self.textbox.insert("end", f"> {text}\n")
        self.textbox.see("end")

    def on_type_change(self):
        self.update_resolution_state()
        self.update_status_info()

    def update_resolution_state(self):
        if self.content_type.get() == "video":
            self.resolution_label.configure(text_color="white")
            self.resolution_menu.configure(state="normal")
        else:
            self.resolution_label.configure(text_color="gray50")
            self.resolution_menu.configure(state="disabled")

    def update_status_info(self, _=None):
        if self.content_type.get() == "video":
            self.status_info.configure(text=f"Formato: MP4 | Resolução: {self.video_resolution.get()}")
        else:
            self.status_info.configure(text="Formato: MP3 | Taxa: 128 kbps")

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Atenção", "O campo de link está vazio!")
            return
        
        titulo_dialogo = "Selecione a pasta para salvar o vídeo" if self.content_type.get() == "video" else "Selecione a pasta para salvar o áudio"
        pasta_destino = filedialog.askdirectory(title=titulo_dialogo)
        
        if not pasta_destino: # Se o usuário cancelar a seleção
            return

        self.download_button.configure(state="disabled", text="PROCESSANDO...")
        # Rodar em segundo plano para não travar a janela
        thread = threading.Thread(target=self.executar_download, args=(url, pasta_destino), daemon=True)
        thread.start()

    def executar_download(self, url, pasta_destino):
        # O ffmpeg ainda precisa estar na pasta onde o SCRIPT/EXE está
        diretorio_script = os.path.dirname(os.path.abspath(__file__))
        
        if self.content_type.get() == "video":
            altura = int(self.video_resolution.get().replace("p", ""))
            ydl_opts = {
                'format': f'(bestvideo[height<={altura}]+bestaudio/best)/best',
                'merge_output_format': 'mp4',
                'ffmpeg_location': diretorio_script,
                'outtmpl': {
                    'default': f'{pasta_destino}/%(title)s.%(ext)s',
                    'playlist': f'{pasta_destino}/%(playlist_title)s/%(title)s.%(ext)s'
                },
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }
        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'ffmpeg_location': diretorio_script, 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'outtmpl': {
                    'default': f'{pasta_destino}/%(title)s.%(ext)s',
                    'playlist': f'{pasta_destino}/%(playlist_title)s/%(title)s.%(ext)s'
                },
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log(f"Iniciando download em: {pasta_destino}")
                ydl.download([url])
                self.log("Finalizado com sucesso!")
                messagebox.showinfo("Sucesso", "Download e conversão concluídos!")
        except Exception as e:
            self.log(f"ERRO: {str(e)}")
        finally:
            self.download_button.configure(state="normal", text="SELECIONAR PASTA E BAIXAR")

if __name__ == "__main__":
    app = QuartetoDownloader()
    app.mainloop()