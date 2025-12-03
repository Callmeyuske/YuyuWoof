import sys
import os
import asyncio
from datetime import datetime

diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(diretorio_raiz)

try:
    from Settings.config import PASTA_SAIDA, ATOR_ATUAL, FALAS, ARQUIVO_FUNDO, MODO_GERACAO
    from Settings.atores import ATORES
    from src.tts_service import gerar_audio_e_legenda
    from src.video_engine import renderizar_video_single, renderizar_video_adventure
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
    nome_sessao = f"{agora.strftime('%Y%m%d_%H-%M')}_{ATOR_ATUAL}_{MODO_GERACAO}"
    caminho_sessao = os.path.join(PASTA_SAIDA, nome_sessao)

    if not os.path.exists(caminho_sessao):
        os.makedirs(caminho_sessao)

    print(f"=== SESSÃO: {MODO_GERACAO} | ATOR: {ATOR_ATUAL} ===")
    
    assets_audio = []
    assets_srt = []

    for i, texto in enumerate(FALAS):
        nome_base = f"Post_{i+1:02d}"
        caminho_audio = os.path.join(caminho_sessao, f"{nome_base}.mp3")
        caminho_legenda = os.path.join(caminho_sessao, f"{nome_base}.srt")
        
        print(f"\n[{i+1}/{len(FALAS)}] Gerando Audio/SRT: {texto[:30]}...")
        await gerar_audio_e_legenda(texto, caminho_audio, caminho_legenda, perfil_ator)
        
        if MODO_GERACAO == "SinglePosts":
            caminho_video = os.path.join(caminho_sessao, f"{nome_base}_Final.mp4")
            print(f"   ---> Renderizando SinglePost: {nome_base}_Final.mp4")
            await renderizar_video_single(caminho_audio, caminho_legenda, ARQUIVO_FUNDO, caminho_video)
            
            # --- CLEANUP (LIXO) ---
            try:
                if os.path.exists(caminho_audio): os.remove(caminho_audio)
                if os.path.exists(caminho_legenda): os.remove(caminho_legenda)
                print("   [Limpeza] Arquivos temporários deletados.")
            except Exception as e:
                print(f"   [Aviso] Falha ao limpar arquivos: {e}")
        
        else: # Adventure
            assets_audio.append(caminho_audio)
            assets_srt.append(caminho_legenda)

    if MODO_GERACAO == "Adventure" and assets_audio:
        print(f"\n--- Iniciando Renderização Adventure Concatenada ---")
        caminho_final = os.path.join(caminho_sessao, "Video_Adventure_Completo.mp4")
        await renderizar_video_adventure(assets_audio, assets_srt, ARQUIVO_FUNDO, caminho_final)

    print(f"\n--- Processo Finalizado ({MODO_GERACAO}) ---")
    print(f"Pasta da sessão: {caminho_sessao}")

if __name__ == "__main__":
    asyncio.run(main())