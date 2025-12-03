import edge_tts
import math
import os

def _formatar_tempo_srt(ticks):
    segundos = ticks / 10_000_000
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milisegundos = int((segundos - int(segundos)) * 1000)
    return f"{horas:02}:{minutos:02}:{segs:02},{milisegundos:03}"

def _criar_srt_customizado(word_events, duracao_total_estimada_s=0, texto_completo=""):
    if not word_events:
        fim_ticks = int(duracao_total_estimada_s * 10_000_000)
        return (
            "1\n"
            f"00:00:00,000 --> {_formatar_tempo_srt(fim_ticks)}\n"
            f"{texto_completo}\n\n"
        )

    srt_output = []
    buffer_palavras = []
    buffer_inicio = 0
    limite_caracteres = 40 
    
    indice = 1

    for i, event in enumerate(word_events):
        offset = event.get('offset') if isinstance(event, dict) else event.offset
        duration = event.get('duration') if isinstance(event, dict) else event.duration
        text = event.get('text') if isinstance(event, dict) else event.text

        if not buffer_palavras:
            buffer_inicio = offset

        buffer_palavras.append(text)
        tamanho_atual = sum(len(w) + 1 for w in buffer_palavras)
        
        if tamanho_atual >= limite_caracteres or i == len(word_events) - 1:
            tempo_fim = offset + duration + 5000000 
            
            linha = f"{indice}\n"
            linha += f"{_formatar_tempo_srt(buffer_inicio)} --> {_formatar_tempo_srt(tempo_fim)}\n"
            linha += f"{' '.join(buffer_palavras)}\n\n"
            srt_output.append(linha)
            
            buffer_palavras = []
            indice += 1

    return "".join(srt_output)

async def gerar_audio_e_legenda(texto: str, caminho_audio: str, caminho_legenda: str, config_ator: dict) -> None:
    communicate = edge_tts.Communicate(
        text=texto,
        voice=config_ator["voice"],
        rate=config_ator["rate"],
        pitch=config_ator["pitch"]
    )

    word_events = []
    audio_data = b""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            word_events.append(chunk)

    with open(caminho_audio, "wb") as file:
        file.write(audio_data)

    duracao_estimada = len(audio_data) / 4000 

    conteudo_srt = _criar_srt_customizado(word_events, duracao_estimada, texto)
    
    with open(caminho_legenda, "w", encoding="utf-8") as file:
        file.write(conteudo_srt)