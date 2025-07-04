import zipfile
import os

def compress_files(files_to_compress, output_zip_name):
    """
    Comprime uma lista de arquivos em um único arquivo ZIP.

    Args:
        files_to_compress (list): Uma lista de caminhos para os arquivos a serem comprimidos.
        output_zip_name (str): O nome do arquivo ZIP de saída.

    Returns:
        str: O caminho para o arquivo ZIP criado.
    """
    with zipfile.ZipFile(output_zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_compress:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
            else:
                print(f"Aviso: Arquivo não encontrado - {file_path}")
    return output_zip_name

def get_compressed_file_list(zip_file_path):
    """
    Retorna uma lista dos nomes dos arquivos dentro de um arquivo ZIP.

    Args:
        zip_file_path (str): O caminho para o arquivo ZIP.

    Returns:
        list: Uma lista de strings com os nomes dos arquivos comprimidos.
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zipf:
            return zipf.namelist()
    except zipfile.BadZipFile:
        print(f"Erro: O arquivo {zip_file_path} não é um arquivo ZIP válido.")
        return []
    except FileNotFoundError:
        print(f"Erro: Arquivo ZIP não encontrado - {zip_file_path}")
        return []





def display_compressed_files(zip_file_path):
    """
    Exibe a lista de arquivos dentro de um arquivo ZIP e pede ao usuário para selecionar um.

    Args:
        zip_file_path (str): O caminho para o arquivo ZIP.

    Returns:
        str or None: O nome do arquivo selecionado pelo usuário, ou None se a seleção for inválida.
    """
    file_list = get_compressed_file_list(zip_file_path)
    if not file_list:
        print("Nenhum arquivo encontrado no ZIP ou o arquivo ZIP é inválido.")
        return None

    print("\nArquivos comprimidos disponíveis:")
    for i, file_name in enumerate(file_list):
        print(f"{i + 1}. {file_name}")

    while True:
        try:
            choice = input("Digite o número do arquivo que deseja descomprimir (ou 'q' para sair): ")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(file_list):
                return file_list[index]
            else:
                print("Seleção inválida. Por favor, digite um número válido.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")





def decompress_file(zip_file_path, file_name, extract_path):
    """
    Descomprime um arquivo específico de um arquivo ZIP.

    Args:
        zip_file_path (str): O caminho para o arquivo ZIP.
        file_name (str): O nome do arquivo a ser descomprimido dentro do ZIP.
        extract_path (str): O diretório para onde o arquivo será extraído.

    Returns:
        str or None: O caminho completo para o arquivo descomprimido, ou None em caso de erro.
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zipf:
            if file_name in zipf.namelist():
                zipf.extract(file_name, extract_path)
                return os.path.join(extract_path, file_name)
            else:
                print(f"Erro: Arquivo '{file_name}' não encontrado no ZIP.")
                return None
    except zipfile.BadZipFile:
        print(f"Erro: O arquivo {zip_file_path} não é um arquivo ZIP válido.")
        return None
    except FileNotFoundError:
        print(f"Erro: Arquivo ZIP não encontrado - {zip_file_path}")
        return None

def recompress_file(zip_file_path, original_file_name, extracted_file_path):
    """
    Recomprime um arquivo de volta para o arquivo ZIP, substituindo a versão antiga.

    Args:
        zip_file_path (str): O caminho para o arquivo ZIP.
        original_file_name (str): O nome original do arquivo dentro do ZIP.
        extracted_file_path (str): O caminho para o arquivo que foi extraído e possivelmente modificado.

    Returns:
        bool: True se a recompressão for bem-sucedida, False caso contrário.
    """
    try:
        # Criar um novo ZIP temporário para evitar problemas de sobrescrita
        temp_zip_path = zip_file_path + ".temp"
        with zipfile.ZipFile(zip_file_path, 'r') as zin:
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename != original_file_name:
                        zout.writestr(item.filename, zin.read(item.filename))
                # Adicionar o arquivo modificado ou o arquivo original se não foi modificado
                zout.write(extracted_file_path, original_file_name)
        
        os.remove(zip_file_path) # Remover o ZIP original
        os.rename(temp_zip_path, zip_file_path) # Renomear o ZIP temporário
        print(f"Arquivo '{original_file_name}' recomprimido com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao recomprimir o arquivo '{original_file_name}': {e}")
        return False





def wait_for_file_close(file_path):
    """
    Simula a espera pelo fechamento de um arquivo, pedindo confirmação ao usuário.

    Args:
        file_path (str): O caminho para o arquivo que está sendo "monitorado".

    Returns:
        bool: True se o usuário confirmar o fechamento, False caso contrário.
    """
    input(f"Pressione Enter quando terminar de usar o arquivo '{os.path.basename(file_path)}' e ele estiver fechado...")
    return True




from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileCloseHandler(FileSystemEventHandler):
    def __init__(self, file_path, callback):
        super().__init__()
        self.file_path = file_path
        self.callback = callback
        self.closed = False

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.file_path:
            # Heurística simples: se o arquivo foi modificado e não está mais sendo escrito,
            # pode indicar que foi fechado. Isso pode não ser 100% preciso para todos os casos.
            # Uma abordagem mais robusta envolveria verificar o handle do arquivo.
            try:
                with open(self.file_path, 'a') as f:
                    pass # Tenta abrir em modo de escrita para ver se está bloqueado
                if not self.closed:
                    print(f"Detectado possível fechamento/salvamento de: {os.path.basename(self.file_path)}")
                    self.closed = True
                    self.callback(self.file_path)
            except IOError:
                pass # Arquivo ainda está em uso

def wait_for_file_close_automatic(file_path, callback):
    event_handler = FileCloseHandler(file_path, callback)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(file_path), recursive=False)
    observer.start()
    print(f"Monitorando o arquivo \'{os.path.basename(file_path)}\' para fechamento automático...")
    try:
        while not event_handler.closed:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()




def generate_test_files(num_files=3, base_size_kb=100, file_types=None):
    """
    Gera arquivos de teste com diferentes tamanhos e tipos.

    Args:
        num_files (int): Número de arquivos a serem gerados.
        base_size_kb (int): Tamanho base em KB para os arquivos.
        file_types (list): Lista de extensões de arquivo a serem usadas (ex: ['txt', 'log', 'csv']).

    Returns:
        list: Uma lista de caminhos para os arquivos gerados.
    """
    if file_types is None:
        file_types = ['txt', 'log', 'csv', 'json', 'xml']

    generated_files = []
    for i in range(num_files):
        file_type = file_types[i % len(file_types)]
        file_name = f"test_file_{i+1}.{file_type}"
        size_bytes = base_size_kb * 1024 + (i * 1024 * 50) # Aumenta o tamanho um pouco para cada arquivo
        
        with open(file_name, 'wb') as f:
            f.write(os.urandom(size_bytes)) # Conteúdo aleatório para dificultar a compressão
        generated_files.append(file_name)
        print(f"Gerado: {file_name} ({size_bytes / 1024:.2f} KB)")
    return generated_files


