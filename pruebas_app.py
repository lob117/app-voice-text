from deepgram import DeepgramClient, PrerecordedOptions

# The API key we created in step 3
DEEPGRAM_API_KEY = '47dabe3fb65aaaa9b1a605272d264340a6b7e4b2'

# Replace with your file path
PATH_TO_FILE = 'ejemplo.wav'

def main():
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(PATH_TO_FILE, 'rb') as buffer_data:
            payload = { 'buffer': buffer_data }

            options = PrerecordedOptions(
                punctuate=True, 
                model="nova-2", 
                language="es"
            )

            response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)
            
            # Extraer solo el texto de la transcripción
            transcript = response.results.channels[0].alternatives[0].transcript
            
            print("Texto transcrito:")
            print(transcript)
            
            # Si quieres guardar el texto en un archivo
            with open('transcripcion.txt', 'w', encoding='utf-8') as f:
                f.write(transcript)
            print("\nTexto guardado en 'transcripcion.txt'")
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {PATH_TO_FILE}")
    except Exception as e:
        print(f"Error durante la transcripción: {e}")

if __name__ == '__main__':
    main()