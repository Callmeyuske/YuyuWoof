import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import sys
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Settings.atores import ATORES
from src.tts_service import gerar_audio_e_legenda
from src.video_engine import renderizar_video_single, renderizar_video_adventure

# Configuração Visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class YuyuWoofApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YuyuWoof_v1")
        self.geometry("700x650")
        self.resizable(True, True)

        # Variáveis
        self.caminho_fundo = None
        self.modo_geracao = ctk.StringVar(value="SinglePosts")
        self.ator_selecionado = ctk.StringVar(value="Template")

        self._montar_layout()

    def _montar_layout(self):
        # --- Título ---
        self.lbl_titulo = ctk.CTkLabel(self, text="YuYuWoof", font=("Roboto", 24, "bold"))
        self.lbl_titulo.pack(pady=15)

        # --- Seleção de Fundo ---
        self.frame_fundo = ctk.CTkFrame(self)
        self.frame_fundo.pack(fill="x", padx=20, pady=5)
        
        self.btn_fundo = ctk.CTkButton(self.frame_fundo, text="Selecionar Fundo (Img/Vid)", command=self.selecionar_fundo, fg_color="#731616", hover_color="#4d0f0f")
        self.btn_fundo.pack(side="left", padx=10, pady=10)
        
        self.lbl_fundo_path = ctk.CTkLabel(self.frame_fundo, text="Nenhum arquivo selecionado", text_color="gray")
        self.lbl_fundo_path.pack(side="left", padx=10)

        # --- Configurações (Ator e Modo) ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(fill="x", padx=20, pady=10)

        # Combo Ator
        ctk.CTkLabel(self.frame_config, text="Ator:").pack(side="left", padx=(10, 5))
        self.combo_ator = ctk.CTkComboBox(self.frame_config, values=list(ATORES.keys()), variable=self.ator_selecionado)
        self.combo_ator.pack(side="left", padx=5)

        # Radio Modo
        ctk.CTkLabel(self.frame_config, text="Modo:").pack(side="left", padx=(20, 5))
        self.radio_single = ctk.CTkRadioButton(self.frame_config, text="SinglePosts", variable=self.modo_geracao, value="SinglePosts")
        self.radio_single.pack(side="left", padx=5)
        self.radio_adv = ctk.CTkRadioButton(self.frame_config, text="Adventure", variable=self.modo_geracao, value="Adventure")
        self.radio_adv.pack(side="left", padx=5)

        # --- Área de Roteiro ---
        ctk.CTkLabel(self, text="Roteiro (Cada linha é um novo post/cena):").pack(anchor="w", padx=25)
        self.textbox_roteiro = ctk.CTkTextbox(self, height=200)
        self.textbox_roteiro.pack(fill="x", padx=20, pady=5)

        # --- Console de Log ---
        ctk.CTkLabel(self, text="Log Infernal:").pack(anchor="w", padx=25)
        self.textbox_log = ctk.CTkTextbox(self, height=100, state="disabled", fg_color="#1a1a1a", text_color="#00ff00")
        self.textbox_log.pack(fill="x", padx=20, pady=5)

        # --- Botão Iniciar ---
        self.btn_start = ctk.CTkButton(self, text="INICIAR RITUAL", command=self.iniciar_thread, height=50, font=("Roboto", 16, "bold"), fg_color="green", hover_color="darkgreen")
        self.btn_start.pack(fill="x", padx=20, pady=20)

    def log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", f"> {mensagem}\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    def selecionar_fundo(self):
        arquivo = filedialog.askopenfilename(filetypes=[("Media", "*.jpg *.png *.gif *.mp4")])
        if arquivo:
            self.caminho_fundo = arquivo
            self.lbl_fundo_path.configure(text=os.path.basename(arquivo), text_color="white")

    def iniciar_thread(self):
        if not self.caminho_fundo:
            self.log("ERRO: Selecione um fundo primeiro.")
            return
        
        texto_raw = self.textbox_roteiro.get("1.0", "end").strip()
        if not texto_raw:
            self.log("ERRO: O roteiro está vazio.")
            return

        # BLOQUEIA O BOTAO = TRAVA TUDO 
        self.btn_start.configure(state="disabled", text="PROCESSANDO...")
        
        falas = [linha.strip() for linha in texto_raw.split('\n') if linha.strip()]

        # Inicia processamento em background para não travar a UI
        threading.Thread(target=self.run_processo, args=(falas,)).start()

    def run_processo(self, falas):
        asyncio.run(self.processo_async(falas))
        # Restaura botão
        self.btn_start.configure(state="normal", text="INICIAR RITUAL")

    async def processo_async(self, falas):
        ator = self.ator_selecionado.get()
        modo = self.modo_geracao.get()
        perfil_ator = ATORES[ator]
        
        # Cria pasta da sessão
        pasta_saida = "audios_sessao" # Hardcoded ou pegue do config
        agora = datetime.now()
        nome_sessao = f"{agora.strftime('%Y%m%d_%H-%M')}_{ator}_{modo}"
        caminho_sessao = os.path.join(pasta_saida, nome_sessao)
        
        if not os.path.exists(caminho_sessao):
            os.makedirs(caminho_sessao)

        self.log(f"Sessão iniciada: {nome_sessao}")
        self.log(f"Modo: {modo} | Fundo: {os.path.basename(self.caminho_fundo)}")

        assets_audio = []
        assets_srt = []

        try:
            for i, texto in enumerate(falas):
                nome_base = f"Post_{i+1:02d}"
                caminho_audio = os.path.join(caminho_sessao, f"{nome_base}.mp3")
                caminho_legenda = os.path.join(caminho_sessao, f"{nome_base}.srt")

                self.log(f"[{i+1}/{len(falas)}] Gerando TTS: {texto[:20]}...")
                await gerar_audio_e_legenda(texto, caminho_audio, caminho_legenda, perfil_ator)

                if modo == "SinglePosts":
                    caminho_video = os.path.join(caminho_sessao, f"{nome_base}_Final.mp4")
                    self.log(f"   -> Renderizando Vídeo...")
                    # Chama função do engine
                    await renderizar_video_single(caminho_audio, caminho_legenda, self.caminho_fundo, caminho_video)
                    
                    # Limpeza
                    if os.path.exists(caminho_audio): os.remove(caminho_audio)
                    if os.path.exists(caminho_legenda): os.remove(caminho_legenda)
                else:
                    assets_audio.append(caminho_audio)
                    assets_srt.append(caminho_legenda)

            if modo == "Adventure" and assets_audio:
                self.log("Concatenando Modo Adventure...")
                caminho_final = os.path.join(caminho_sessao, "Video_Adventure_Completo.mp4")
                await renderizar_video_adventure(assets_audio, assets_srt, self.caminho_fundo, caminho_final)

            self.log(f"PROCESSO CONCLUÍDO! Pasta: {nome_sessao}")
            os.startfile(caminho_sessao) # Abre a pasta automaticamente no Windows

        except Exception as e:
            self.log(f"ERRO FATAL: {str(e)}")
            print(e)

if __name__ == "__main__":
    app = YuyuWoofApp()
    app.mainloop()