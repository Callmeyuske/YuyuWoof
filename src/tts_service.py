import edge_tts

async def gerar_audio(texto: str, caminho_arquivo: str, config_ator: dict) -> None:
    communicate = edge_tts.Communicate(
        text=texto,
        voice=config_ator["voice"],
        rate=config_ator["rate"],
        pitch=config_ator["pitch"]
    )
    await communicate.save(caminho_arquivo)