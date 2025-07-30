import speech_recognition as sr
from pydub import AudioSegment
import os
from tqdm import tqdm
import math

def segment_audio(audio_file_path, segment_duration_ms=90000):  # 90 segundos = 1.5 minutos
    """
    Segmenta el audio en fragmentos de duración específica
    """
    print("Cargando archivo de audio...")
    audio = AudioSegment.from_file(audio_file_path)
    
    # Calcular número de segmentos
    total_duration = len(audio)
    num_segments = math.ceil(total_duration / segment_duration_ms)
    
    print(f"Duración total: {total_duration/1000:.2f} segundos")
    print(f"Creando {num_segments} segmentos de {segment_duration_ms/1000} segundos cada uno...")
    
    segments = []
    
    # Crear barra de progreso para segmentación
    with tqdm(total=num_segments, desc="Segmentando audio", unit="segmento") as pbar:
        for i in range(num_segments):
            start_time = i * segment_duration_ms
            end_time = min((i + 1) * segment_duration_ms, total_duration)
            
            segment = audio[start_time:end_time]
            segment_filename = f"temp_segment_{i+1}.wav"
            segment.export(segment_filename, format="wav")
            segments.append(segment_filename)
            
            pbar.update(1)
    
    return segments

def transcribe_segments(segments):
    """
    Transcribe cada segmento de audio
    """
    r = sr.Recognizer()
    transcriptions = []
    
    print("\nIniciando transcripción de segmentos...")
    
    # Crear barra de progreso para transcripción
    with tqdm(total=len(segments), desc="Transcribiendo", unit="segmento") as pbar:
        for i, segment_file in enumerate(segments):
            try:
                with sr.AudioFile(segment_file) as source:
                    # Ajustar para ruido ambiente en el primer segmento
                    if i == 0:
                        r.adjust_for_ambient_noise(source, duration=1)
                    
                    audio_data = r.record(source)
                    
                    # Transcribir usando Google Speech Recognition
                    text = r.recognize_google(audio_data, language='es-ES')
                    transcriptions.append(f"Segmento {i+1}: {text}")
                    
            except sr.UnknownValueError:
                transcriptions.append(f"Segmento {i+1}: [Audio no reconocible]")
            except sr.RequestError as e:
                transcriptions.append(f"Segmento {i+1}: [Error de servicio: {e}]")
            except Exception as e:
                transcriptions.append(f"Segmento {i+1}: [Error: {e}]")
            
            pbar.update(1)
    
    return transcriptions

def cleanup_temp_files(segments):
    """
    Elimina archivos temporales
    """
    print("\nLimpiando archivos temporales...")
    for segment_file in segments:
        try:
            if os.path.exists(segment_file):
                os.remove(segment_file)
        except Exception as e:
            print(f"No se pudo eliminar {segment_file}: {e}")

def main():
    # Ruta del archivo original
    audio_file_path = "ejemplo_oficina_mejor.wav"
    
    # Verificar que el archivo existe
    if not os.path.exists(audio_file_path):
        print(f"Error: No se encontró el archivo {audio_file_path}")
        return
    
    try:
        # Segmentar el audio en fragmentos de 1.5 minutos
        segments = segment_audio(audio_file_path, segment_duration_ms=90000)
        
        # Transcribir cada segmento
        transcriptions = transcribe_segments(segments)
        
        # Mostrar resultados
        print("\n" + "="*50)
        print("TRANSCRIPCIÓN COMPLETA")
        print("="*50)
        
        full_transcription = ""
        for transcription in transcriptions:
            print(transcription)
            print("-" * 30)
            # Extraer solo el texto sin el prefijo "Segmento X:"
            if ": " in transcription and not transcription.endswith("]"):
                text_part = transcription.split(": ", 1)[1]
                full_transcription += text_part + " "
        
        # Guardar transcripción completa en archivo
        output_file = "transcripcion_completa.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("TRANSCRIPCIÓN POR SEGMENTOS:\n")
            f.write("="*50 + "\n\n")
            for transcription in transcriptions:
                f.write(transcription + "\n\n")
            
            f.write("\nTRANSCRIPCIÓN CONTINUA:\n")
            f.write("="*50 + "\n")
            f.write(full_transcription.strip())
        
        print(f"\nTranscripción guardada en: {output_file}")
        
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
    
    finally:
        # Limpiar archivos temporales
        if 'segments' in locals():
            cleanup_temp_files(segments)

if __name__ == "__main__":
    main()