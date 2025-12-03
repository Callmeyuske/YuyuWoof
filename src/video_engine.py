import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
import os

caminho_magick_padrao = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
if os.path.exists(caminho_magick_padrao):
    change_settings({"IMAGEMAGICK_BINARY": caminho_magick_padrao})

def gerar_generator_legenda(txt):
    return TextClip(
        txt, 
        font='Arial', 
        fontsize=55, 
        color='white', 
        stroke_color='black', 
        stroke_width=2, 
        method='caption',
        size=(900, None), 
        align='center'
    )

def _criar_clip_base(caminho_audio, caminho_fundo):
    audio_clip = AudioFileClip(caminho_audio)
    duracao = audio_clip.duration

    if caminho_fundo.endswith(('.jpg', '.jpeg', '.png')):
        video_fundo = ImageClip(caminho_fundo).set_duration(duracao)
        
        video_fundo = video_fundo.resize(height=1920)
        video_fundo = video_fundo.crop(x1=0, y1=0, width=1080, height=1920, x_center=video_fundo.w/2, y_center=video_fundo.h/2)
    else:
        video_fundo = VideoFileClip(caminho_fundo)
        if video_fundo.duration < duracao:
            video_fundo = vfx.loop(video_fundo, duration=duracao)
        else:
            video_fundo = video_fundo.subclip(0, duracao)
            
        video_fundo = video_fundo.resize(height=1920)
        video_fundo = video_fundo.crop(x1=0, y1=0, width=1080, height=1920, x_center=video_fundo.w/2, y_center=video_fundo.h/2)
            
    return video_fundo.set_audio(audio_clip), audio_clip, video_fundo

def _preparar_srt_para_windows(caminho_srt_utf8):
    try:
        with open(caminho_srt_utf8, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        caminho_temp = caminho_srt_utf8.replace('.srt', '_win.srt')
        with open(caminho_temp, 'w', encoding='cp1252', errors='replace') as f:
            f.write(conteudo)
            
        return caminho_temp
    except Exception as e:
        print(f"AVISO ENCODING: {e}")
        return caminho_srt_utf8

async def montar_video_final_concatenado(lista_audios, lista_srts, caminho_fundo, caminho_saida_final):
    clips_para_juntar = []
    resources_to_close = []
    arquivos_temporarios = []

    try:
        print(f"--- MONTAGEM FINAL ({len(lista_audios)} partes) ---")

        for i, (audio_path, srt_path) in enumerate(zip(lista_audios, lista_srts)):
            print(f"Processando parte {i+1}...")
            video_base, ac, vfc = _criar_clip_base(audio_path, caminho_fundo)
            resources_to_close.extend([ac, vfc])

            if os.path.exists(srt_path) and os.path.getsize(srt_path) > 0:
                try:
                    srt_compativel = _preparar_srt_para_windows(srt_path)
                    if srt_compativel != srt_path:
                        arquivos_temporarios.append(srt_compativel)
                    
                    legendas = SubtitlesClip(srt_compativel, gerar_generator_legenda)
                    legendas = legendas.set_position(('center', 'center'))
                    
                    clip_pronto = CompositeVideoClip([video_base, legendas])
                except Exception as e:
                    print(f"FALHA LEGENDA: {e}")
                    clip_pronto = video_base
            else:
                clip_pronto = video_base
            
            clips_para_juntar.append(clip_pronto)

        if clips_para_juntar:
            print("Renderizando vídeo final...")
            video_final_zao = concatenate_videoclips(clips_para_juntar, method="compose")
            video_final_zao.write_videofile(
                caminho_saida_final, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac', 
                threads=4, 
                preset='ultrafast',
                logger='bar'
            )
            video_final_zao.close()
        
    except Exception as e:
        print(f"ERRO CRÍTICO NA MONTAGEM: {e}")
    finally:
        for clip in clips_para_juntar:
            try: clip.close()
            except: pass
        for res in resources_to_close:
            try: res.close()
            except: pass
            
        for arq in arquivos_temporarios:
            try:
                if os.path.exists(arq):
                    os.remove(arq)
            except: pass