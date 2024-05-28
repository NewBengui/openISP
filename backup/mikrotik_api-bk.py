import paramiko

MIKROTIK_HOST = '10.10.10.1'
MIKROTIK_USER = 'admin'
PRIVATE_KEY_FILE = 'private.pem'

class MikroTikError(Exception):
    pass

def connect_to_mikrotik():
    try:
        private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_FILE)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=MIKROTIK_HOST, username=MIKROTIK_USER, pkey=private_key)
        return ssh_client
    except Exception as e:
        error_message = f"Failed to connect to MikroTik: {e}"
        print(error_message)
        raise MikroTikError(error_message)

def activate_user_profile(reference, value):
    ssh_client = None
    try:
        ssh_client = connect_to_mikrotik()
        
        # Determinar o perfil com base no valor
        profile_mapping = {
            "20520": "10MB",
            "28500": "15MB"
        }
        
        profile = profile_mapping.get(value)
        
        if not profile:
            error_message = f"Invalid value for determining profile: {value}"
            print(error_message)
            raise MikroTikError(error_message)
        
        # Executar o comando para adicionar um novo user-profile
        command = f'/tool user-manager user-profile add profile="{profile}" user="{reference}"'
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8")
        if output:
            print(output)
        else:
            print("No output from MikroTik.")
    except MikroTikError as e:
        print(e)
        raise
    except Exception as e:
        error_message = f"Failed to activate user profile: {e}"
        print(error_message)
        raise MikroTikError(error_message)
    finally:
        if ssh_client:
            ssh_client.close()
