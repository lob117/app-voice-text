import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import speech_recognition as sr
from pydub import AudioSegment
import os
import math
import threading
from datetime import datetime

# Configurar el tema de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AudioTranscriptionApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Transcriptor de Audio - Segmentado")
        
        # Configurar ventana en pantalla completa maximizada
        self.root.state('zoomed')  # Para Windows
        # Para otros sistemas operativos como alternativa:
        # self.root.attributes('-zoomed', True)  # Linux
        # self.root.attributes('-fullscreen', False)  # macOS
        
        self.root.resizable(True, True)
        
        # Variables de control
        self.is_processing = False
        self.is_paused = False
        self.current_segment = 0
        self.total_segments = 0
        self.segments = []
        self.transcriptions = []
        
        # Variables de entrada
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.segment_duration = 90  # 90 segundos fijo (1.5 minutos)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎤 Transcriptor de Audio Segmentado", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Frame de configuración
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Archivo de entrada
        input_frame = ctk.CTkFrame(config_frame)
        input_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(input_frame, text="📁 Archivo de Audio:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        input_file_frame = ctk.CTkFrame(input_frame)
        input_file_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.input_entry = ctk.CTkEntry(input_file_frame, textvariable=self.input_file, placeholder_text="Selecciona el archivo de audio...")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        input_btn = ctk.CTkButton(input_file_frame, text="Buscar", command=self.select_input_file, width=80)
        input_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Carpeta de salida
        output_frame = ctk.CTkFrame(config_frame)
        output_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(output_frame, text="💾 Carpeta de Salida:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        output_file_frame = ctk.CTkFrame(output_frame)
        output_file_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.output_entry = ctk.CTkEntry(output_file_frame, textvariable=self.output_folder)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        output_btn = ctk.CTkButton(output_file_frame, text="Buscar", command=self.select_output_folder, width=80)
        output_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Frame de progreso general (NUEVO)
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Etiqueta de estado general
        self.general_status_label = ctk.CTkLabel(progress_frame, text="Listo para comenzar", font=ctk.CTkFont(size=14, weight="bold"))
        self.general_status_label.pack(pady=(15, 5))
        
        # Barra de progreso general
        self.general_progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self.general_progress_bar.pack(fill="x", padx=20, pady=(0, 5))
        self.general_progress_bar.set(0)
        
        # Etiqueta de progreso detallado
        self.detailed_progress_label = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=12))
        self.detailed_progress_label.pack(pady=(0, 15))
        
        # Frame de controles
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botones de control
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(
            button_frame, 
            text="▶️ Iniciar Transcripción", 
            command=self.start_transcription,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.pause_btn = ctk.CTkButton(
            button_frame, 
            text="⏸️ Pausar", 
            command=self.pause_transcription,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            button_frame, 
            text="⏹️ Detener", 
            command=self.stop_transcription,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        
        # Área de texto para resultados
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill="both", expand=True, padx=20)
        
        ctk.CTkLabel(result_frame, text="📝 Resultados de Transcripción:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(result_frame, height=200)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.wav *.mp3 *.m4a *.flac *.aac"),
                ("Todos los archivos", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)
            
    def start_transcription(self):
        if not self.input_file.get():
            messagebox.showerror("Error", "Por favor selecciona un archivo de audio")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "El archivo de audio no existe")
            return
            
        self.is_processing = True
        self.is_paused = False
        self.current_segment = 0
        self.transcriptions = []
        
        # Actualizar botones
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        
        # Limpiar resultados anteriores
        self.result_text.delete("1.0", "end")
        
        # Resetear barra de progreso
        self.general_progress_bar.set(0)
        
        # Iniciar transcripción en hilo separado
        thread = threading.Thread(target=self.transcription_process)
        thread.daemon = True
        thread.start()
        
    def pause_transcription(self):
        if self.is_processing:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_btn.configure(text="▶️ Continuar")
                self.general_status_label.configure(text="⏸️ Proceso pausado")
            else:
                self.pause_btn.configure(text="⏸️ Pausar")
                
    def stop_transcription(self):
        self.is_processing = False
        self.is_paused = False
        
        # Resetear botones
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸️ Pausar")
        self.stop_btn.configure(state="disabled")
        
        self.general_status_label.configure(text="❌ Proceso detenido")
        self.cleanup_temp_files()
        
    def transcription_process(self):
        try:
            # FASE 1: Segmentar audio
            self.update_general_progress("🔪 Segmentando archivo de audio...", 0)
            self.segments = self.segment_audio()
            
            if not self.is_processing:
                return
                
            self.total_segments = len(self.segments)
            
            # FASE 2: Transcribir segmentos
            self.update_general_progress("🎤 Iniciando transcripción de segmentos...", 0.1)
            r = sr.Recognizer()
            
            for i, segment_file in enumerate(self.segments):
                if not self.is_processing:
                    break
                    
                # Esperar si está pausado
                while self.is_paused and self.is_processing:
                    threading.Event().wait(0.1)
                    
                if not self.is_processing:
                    break
                    
                self.current_segment = i + 1
                
                # Calcular progreso general (10% para segmentación + 90% para transcripción)
                transcription_progress = (i + 1) / self.total_segments
                general_progress = 0.1 + (0.9 * transcription_progress)
                
                self.update_general_progress(f"🎤 Transcribiendo segmento {self.current_segment} de {self.total_segments}", general_progress)
                
                try:
                    with sr.AudioFile(segment_file) as source:
                        if i == 0:
                            r.adjust_for_ambient_noise(source, duration=1)
                        
                        audio_data = r.record(source)
                        text = r.recognize_google(audio_data, language='es-ES')
                        
                        transcription = f"Segmento {i+1}: {text}"
                        self.transcriptions.append(transcription)
                        
                        # Mostrar en tiempo real
                        self.root.after(0, self.update_results, transcription)
                        
                except sr.UnknownValueError:
                    transcription = f"Segmento {i+1}: [Audio no reconocible]"
                    self.transcriptions.append(transcription)
                    self.root.after(0, self.update_results, transcription)
                except Exception as e:
                    transcription = f"Segmento {i+1}: [Error: {str(e)}]"
                    self.transcriptions.append(transcription)
                    self.root.after(0, self.update_results, transcription)
                
                # Actualizar barra de progreso general
                progress = (i + 1) / self.total_segments
                general_progress = 0.1 + (0.9 * progress)
                
            if self.is_processing:
                self.update_general_progress("💾 Guardando transcripción...", 0.95)
                self.save_transcription()
                self.root.after(0, self.transcription_complete)
                
        except Exception as e:
            self.root.after(0, self.show_error, f"Error durante la transcripción: {str(e)}")
        finally:
            self.root.after(0, self.cleanup_temp_files)
            
    def segment_audio(self):
        audio = AudioSegment.from_file(self.input_file.get())
        segment_duration_ms = self.segment_duration * 1000
        
        total_duration = len(audio)
        num_segments = math.ceil(total_duration / segment_duration_ms)
        
        segments = []
        temp_folder = os.path.join(self.output_folder.get(), "temp_segments")
        os.makedirs(temp_folder, exist_ok=True)
        
        for i in range(num_segments):
            if not self.is_processing:
                break
                
            # Actualizar progreso de segmentación
            segmentation_progress = (i + 1) / num_segments * 0.1  # 10% del progreso total
            self.root.after(0, self.update_general_progress, f"🔪 Creando segmento {i+1} de {num_segments}...", segmentation_progress)
            
            start_time = i * segment_duration_ms
            end_time = min((i + 1) * segment_duration_ms, total_duration)
            
            segment = audio[start_time:end_time]
            segment_filename = os.path.join(temp_folder, f"segment_{i+1:03d}.wav")
            segment.export(segment_filename, format="wav")
            segments.append(segment_filename)
            
        return segments
        
    def update_general_progress(self, message, progress):
        """Actualiza la barra de progreso general y su mensaje"""
        self.root.after(0, self.general_status_label.configure, {"text": message})
        self.root.after(0, self.general_progress_bar.set, progress)
        self.root.after(0, self.detailed_progress_label.configure, {"text": f"Progreso general: {progress*100:.1f}%"})
        
    def update_progress(self, message):
        """Método mantenido para compatibilidad pero ya no usado"""
        pass
        
    def update_results(self, transcription):
        self.result_text.insert("end", transcription + "\n\n")
        self.result_text.see("end")
        
    def save_transcription(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_folder.get(), f"transcripcion_{timestamp}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("TRANSCRIPCIÓN DE AUDIO SEGMENTADO\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Archivo original: {self.input_file.get()}\n")
            f.write(f"Duración por segmento: {self.segment_duration} segundos\n")
            f.write(f"Fecha de transcripción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for transcription in self.transcriptions:
                f.write(transcription + "\n\n")
                
            # Transcripción continua
            f.write("\nTRANSCRIPCIÓN CONTINUA:\n")
            f.write("=" * 50 + "\n")
            full_text = ""
            for transcription in self.transcriptions:
                if ": " in transcription and not transcription.endswith("]"):
                    text_part = transcription.split(": ", 1)[1]
                    full_text += text_part + " "
            f.write(full_text.strip())
            
        self.root.after(0, self.show_info, f"Transcripción guardada en:\n{output_file}")
        
    def transcription_complete(self):
        self.update_general_progress("✅ ¡Transcripción completada exitosamente!", 1.0)
        self.stop_transcription()
        
    def cleanup_temp_files(self):
        temp_folder = os.path.join(self.output_folder.get(), "temp_segments")
        if os.path.exists(temp_folder):
            for file in os.listdir(temp_folder):
                try:
                    os.remove(os.path.join(temp_folder, file))
                except:
                    pass
            try:
                os.rmdir(temp_folder)
            except:
                pass
                
    def show_error(self, message):
        messagebox.showerror("Error", message)
        
    def show_info(self, message):
        messagebox.showinfo("Información", message)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AudioTranscriptionApp()
    app.run()