# sftp_utils.py

import os
import json
import paramiko
from datetime import datetime
from database_utils import save_to_mongodb
from mikrotik_api import activate_user_profile

# Definição das configurações do SFTP
SFTP_HOST = '104.255.216.220'
SFTP_PORT = 22
SFTP_USER = 'odoo'
SFTP_PASSWORD = 'Luanda2020#'
REMOTE_DIR = '/home/odoo/emis'
LOCAL_JSON_DIR = 'data'  # Subpasta local para os arquivos JSON
BACKUP_DIR = '/home/odoo/emis/backup'  # Pasta de backup

def file_exists(sftp, directory, filename):
    try:
        sftp.stat(f"{directory}/{filename}")
        return True
    except FileNotFoundError:
        return False

def fetch_sftp_files():
    try:
        # Conexão com o servidor SFTP
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Verifica se o diretório remoto existe
        try:
            sftp.chdir(REMOTE_DIR)
        except IOError:
            error_message = f"O diretório {REMOTE_DIR} não existe no servidor SFTP."
            print(error_message)
            raise FileNotFoundError(error_message)

        files_data = []
        today = datetime.today().strftime('%d-%b-%Y')
        json_filename = os.path.join(LOCAL_JSON_DIR, f"{today}.json")

        for filename in sftp.listdir():
            if filename.endswith('.txt'):
                file_path = f"{REMOTE_DIR}/{filename}"
                try:
                    with sftp.file(file_path, 'r') as file:
                        file_content = []
                        for line in file:
                            data = line.strip().split('|')
                            if len(data) == 7:
                                file_content.append({
                                    "Entidade": data[0],
                                    "Referência": data[1],
                                    "Contrato": data[2],
                                    "Transação": data[3],
                                    "Valor": data[4],
                                    "Data": data[5],
                                    "Estado": data[6],
                                })
                            else:
                                print(f"Linha malformada no arquivo {filename}: {line.strip()}")
                        # Salvando os dados no arquivo JSON local
                        if file_content:
                            files_data.extend(file_content)
                            with open(json_filename, 'a', encoding='utf-8') as json_file:
                                for item in file_content:
                                    json.dump(item, json_file, ensure_ascii=False)
                                    json_file.write('\n')
                            # Movendo o arquivo para a pasta de backup
                            backup_filename = filename
                            while file_exists(sftp, BACKUP_DIR, backup_filename):
                                # If file with the same name exists, append current date and time
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
                            sftp.rename(file_path, f"{BACKUP_DIR}/{backup_filename}")
                            print(f"Arquivo {filename} movido para a pasta de backup como {backup_filename}.")
                except IOError as e:
                    error_message = f"Falha ao ler o arquivo {filename}: {e}"
                    print(error_message)
                    raise IOError(error_message)

        sftp.close()
        transport.close()

        if files_data:
            # Save data to MongoDB
            save_to_mongodb(files_data)

        if not files_data:
            print("Nenhum dado encontrado nos arquivos SFTP.")
            return []

        return files_data

    except paramiko.SSHException as e:
        error_message = f"Falha ao conectar ao servidor SFTP: {e}"
        print(error_message)
        raise ConnectionError(error_message)
    except FileNotFoundError as e:
        # Se o diretório remoto não existir
        raise e
    except IOError as e:
        # Se houver erro ao ler o arquivo
        raise e
    except Exception as e:
        # Para outros erros inesperados
        error_message = f"Ocorreu um erro inesperado: {e}"
        print(error_message)
        raise Exception(error_message)
