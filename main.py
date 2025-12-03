import sys
import os
import asyncio
from datetime import datetime

diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(diretorio_raiz)

try:
    from Settings.config import PASTA_SAIDA, ATOR_ATUAL, FALAS, ARQUIVO_FUNDO
    from Settings.atores import ATORES
    from src.tts_service import gerar_audio_e_legenda
    from src.video_engine import montar_video_final_concatenado
except ImportError as e:
    print(f"Erro de importação: {e}")
    sys.exit(1)

async def main():
    if ATOR_ATUAL not in ATORES:
        print(f"ERRO CRÍTICO: Ator inexistente.")
        sys.exit(1)
        
    if not os.path.exists(ARQUIVO_FUNDO):
        print(f"ERRO: Arquivo de fundo não encontrado.")
        sys.exit(1)

    perfil_ator = ATORES[ATOR_ATUAL]
    agora = datetime.now()
    nome_sessao = f"{agora.strftime('%Y%m%d_%H-%M')}_{ATOR_ATUAL}"
    caminho_sessao = os.path.join(PASTA_SAIDA, nome_sessao)

    if not os.path.exists(caminho_sessao):
        os.makedirs(caminho_sessao)

    print(f"=== SESSÃO VIDEO FACTORY: {ATOR_ATUAL} ===")
    
    assets_audio = []
    assets_srt = []

    for i, texto in enumerate(FALAS):
        nome_base = f"Video_{i+1:02d}"
        caminho_audio = os.path.join(caminho_sessao, f"{nome_base}.mp3")
        caminho_legenda = os.path.join(caminho_sessao, f"{nome_base}.srt")

        print(f"\n[{i+1}/{len(FALAS)}] Gerando Audio/SRT: {texto[:30]}...")
        
        await gerar_audio_e_legenda(texto, caminho_audio, caminho_legenda, perfil_ator)
        
        assets_audio.append(caminho_audio)
        assets_srt.append(caminho_legenda)

    if assets_audio:
        print(f"\n--- Iniciando Renderização do Vídeo Completo ---")
        caminho_final_legendado = os.path.join(caminho_sessao, "Video_Final_Legendado.mp4")
        await montar_video_final_concatenado(assets_audio, assets_srt, ARQUIVO_FUNDO, caminho_final_legendado)

    print(f"\n--- Processo Finalizado ---")
    print(f"Pasta da sessão: {caminho_sessao}")

if __name__ == "__main__":
    asyncio.run(main())