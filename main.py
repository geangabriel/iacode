import os
import shutil
from compressor import compress_files, display_compressed_files, decompress_file, recompress_file, get_compressed_file_list, wait_for_file_close_automatic, generate_test_files

TEMP_DIR = "temp_extracted"

def setup_environment():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def cleanup_environment():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    # Remover arquivos de teste gerados
    for f in os.listdir("."):
        if f.startswith("test_file_"):
            os.remove(f)

def handle_file_closed(file_path):
    print(f"\nArquivo {os.path.basename(file_path)} foi fechado. Recomprimindo...")
    zip_file_name = "meus_arquivos.zip"
    original_file_name = os.path.basename(file_path)
    recompress_file(zip_file_name, original_file_name, file_path)
    os.remove(file_path)

def main():
    setup_environment()
    zip_file_name = "meus_arquivos.zip"

    print("\n--- Gerando arquivos de teste ---")
    test_files = generate_test_files(num_files=5, base_size_kb=500)

    print("\n--- Comprimindo arquivos ---")
    start_time = time.time()
    compress_files(test_files, zip_file_name)
    end_time = time.time()
    print(f"Arquivos comprimidos em: {zip_file_name} (Tempo: {end_time - start_time:.2f} segundos)")

    while True:
        print("\n--- Gerenciador de Arquivos Comprimidos ---")
        selected_file = display_compressed_files(zip_file_name)

        if selected_file:
            print(f"\nDescomprimindo: {selected_file}")
            start_time = time.time()
            extracted_file_path = decompress_file(zip_file_name, selected_file, TEMP_DIR)
            end_time = time.time()
            print(f"Arquivo descomprimido para: {extracted_file_path} (Tempo: {end_time - start_time:.2f} segundos)")

            if extracted_file_path:
                wait_for_file_close_automatic(extracted_file_path, handle_file_closed)
            else:
                print("Não foi possível descomprimir o arquivo selecionado.")
        else:
            print("Saindo do gerenciador de arquivos.")
            break

    cleanup_environment()
    print("\n--- Operação concluída ---")

if __name__ == "__main__":
    import time
    main()


