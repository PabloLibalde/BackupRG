from src.backup import (
    ler_config, obter_backups, executar_backup,
    compactar_arquivo, mover_arquivo, setup_logger, limpar_nome
)
import logging
import os
from datetime import datetime

def main():
    setup_logger()
    logging.info("Iniciando rotina de backup...")

    try:
        config = ler_config()
        backups = obter_backups(config)
        gbak_path = config["global"]["gbak_path"]
        comando_base = config["global"]["backup_command"]

        for db in backups:
            section = db["section"]
            logging.info(f"Processando: {section}")

            # Executa o backup
            executar_backup({
                "gbak_path": gbak_path,
                "database_path": db["database_path"],
                "backup_path": db["backup_path"],
                "backup_command": comando_base
            })
            logging.info(f"{section} - Backup gerado com sucesso.")

            # Compacta
            nome_rar = limpar_nome(section)
            nome_rar = f"{nome_rar}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.rar"
            compactar_arquivo(db["backup_path"], nome_rar)

            # Remove o .fbk após zipar
            try:
                os.remove(db["backup_path"])
                logging.info(f"{section} - Arquivo .fbk removido: {db['backup_path']}")
            except Exception as e:
                logging.warning(f"{section} - Não foi possível remover o .fbk: {e}")

            # Move para destino final
            destino_final = os.path.join(db["final_destination"], nome_rar)
            mover_arquivo(nome_rar, destino_final)
            logging.info(f"{section} - Backup finalizado: {db['final_destination']}")
        
        logging.info("Todos os backups foram realizados com sucesso.")
    except Exception as e:
        logging.exception("Erro geral no processo de backup!")

if __name__ == "__main__":
    main()
