import sys
import os
import asyncio
from datetime import datetime

diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(diretorio_raiz)

try:
    from Settings.config import PASTA_SAIDA, ATOR_ATUAL, FALAS
    from Settings.atores import ATORES
    from src.tts_service import gerar_audio
except ImportError as e:
    print(f"Erro de importação: {e}")
    sys.exit(1)

async def main():
    if ATOR_ATUAL not in ATORES:
        print(f"ERRO CRÍTICO: O ator '{ATOR_ATUAL}' não foi encontrado em Settings/atores.py")
        sys.exit(1)

    perfil_ator = ATORES[ATOR_ATUAL]
    
    agora = datetime.now()
    nome_subpasta = f"{agora.strftime('%Y%m%d_%H-%M')}_{ATOR_ATUAL}"
    
    caminho_final = os.path.join(PASTA_SAIDA, nome_subpasta)

    if not os.path.exists(caminho_final):
        os.makedirs(caminho_final)

    print(f"Sessão iniciada para Ator: {ATOR_ATUAL}")
    print(f"Configuração: {perfil_ator}")
    print(f"Salvando em: {caminho_final}\n")

    for i, texto in enumerate(FALAS):
        nome_arquivo = os.path.join(caminho_final, f"Audio_{i+1:02d}.mp3")
        print(f"[{i+1}/{len(FALAS)}] Renderizando: {nome_arquivo}...")
        await gerar_audio(texto, nome_arquivo, perfil_ator)

    print("\n--- Renderização concluída com sucesso ---")

if __name__ == "__main__":
    asyncio.run(main())