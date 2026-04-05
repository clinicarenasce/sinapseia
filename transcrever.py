from faster_whisper import WhisperModel 
import os 
 
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8") 
 
audio_path = r"C:\Users\conta\Desktop\meu_audio.ma4.m4a" 
 
segments, info = model.transcribe(audio_path, language="pt") 
 
print(f"Idioma detectado: {info.language}") 
print("---") 
 
txt_path = os.path.splitext(audio_path)[0] + ".txt" 
with open(txt_path, "w", encoding="utf-8") as f: 
    for segment in segments: 
        print(f"[{segment.start:.1f}s] {segment.text}") 
        f.write(f"[{segment.start:.1f}s] {segment.text}\n") 
 
print(f"\nTranscricao salva em: {txt_path}") 
