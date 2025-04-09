import subprocess
import logging
import shutil
import zipfile
import sys
import os
import configparser
import unicodedata
from datetime import datetime

def get_app_path():
    """Retorna o caminho da pasta onde está o .py ou .exe"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def gerar_config_padrao(caminho):
    config = configparser.ConfigParser()

    config["global"] = {
        "gbak_path": "C:\\HQBird\\Firebird30\\gbak.exe",
        "backup_command": '-user SYSDBA -pas masterkey -g -l -b -v -z -par 12 "{db}" "{fbk}"',
        "rar_temp_dir": "C:\RGSystem\BackupRG"
    }

    config["database1"] = {
        "database_path": "C:\\dados\\banco1.fdb",
        "backup_path": "C:\\temp\\banco1.fbk",
        "final_destination": "C:\\backups\\banco1.zip"
    }

    config["database2"] = {
        "database_path": "C:\\dados\\banco2.fdb",
        "backup_path": "C:\\temp\\banco2.fbk",
        "final_destination": "C:\\backups\\banco2.zip"
    }

    with open(caminho, "w", encoding="utf-8") as f:
        config.write(f)
    logging.info(f"Arquivo de configuração padrão criado: {caminho}")

def ler_config(filename="config.conf"):
    config_path = os.path.join(get_app_path(), filename)

    if not os.path.exists(config_path):
        gerar_config_padrao(config_path)

    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8-sig')
    return config

def obter_backups(config):
    backups = []
    for section in config.sections():
        if section == "global":
            continue
        backups.append({
            "database_path": config[section]["database_path"],
            "backup_path": config[section]["backup_path"],
            "final_destination": config[section]["final_destination"],
            "section": section
        })
    return backups

def executar_backup(cfg):
    comando = cfg["backup_command"].format(
        db=cfg["database_path"],
        fbk=cfg["backup_path"]
    )
    full_command = f'"{cfg["gbak_path"]}" {comando}'
    logging.info(f"Executando comando: {full_command}")
    
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        logging.error(f"Erro no backup: {result.stderr}")
        raise Exception("Falha no backup")

    logging.info("Backup concluído com sucesso.")

def compactar_arquivo(fbk_path, nome_rar):
    rar_path = shutil.which("rar") or "C:\\Program Files\\WinRAR\\rar.exe"
    
    if not os.path.exists(rar_path):
        raise FileNotFoundError("WinRAR não encontrado. Verifique o caminho para 'rar.exe'.")

    comando = f'"{rar_path}" a -ep1 -m5 "{nome_rar}" "{fbk_path}"'
    logging.info(f"Compactando com: {comando}")
    
    result = subprocess.run(comando, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Erro na compactação: {result.stderr}")
        raise Exception("Erro ao compactar o arquivo")

    logging.info(f"Compactação concluída: {nome_rar}")

def mover_arquivo(origem_rar, destino_final):
    os.makedirs(os.path.dirname(destino_final), exist_ok=True)
    logging.info(f"Movendo {origem_rar} para {destino_final}")
    shutil.move(origem_rar, destino_final)

def setup_logger():
    log_path = os.path.join(get_app_path(), "backup.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def limpar_nome(nome):
    # Remove acentos e espaços, transforma em MAIÚSCULO
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome.replace(' ', '').upper()
