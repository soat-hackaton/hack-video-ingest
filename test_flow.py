import os
import requests
import sys

# Configuração
API_URL = "http://localhost:8000/api/v1"
FILE_NAME = "video_teste.mp4"
CONTENT_TYPE = "video/mp4"

def create_dummy_video():
    """Cria um vídeo fake de 1MB se ele não existir"""
    if not os.path.exists(FILE_NAME):
        print(f"🎥 Criando arquivo fake {FILE_NAME} de 1MB...")
        with open(FILE_NAME, "wb") as f:
            f.write(os.urandom(1024 * 1024)) # 1MB de dados aleatórios

def run_test():
    # 1. Criar arquivo dummy se não existir
    create_dummy_video()

    print(f"--- 1. Solicitando URL de Upload ({FILE_NAME}) ---")
    try:
        req_response = requests.post(f"{API_URL}/request-upload", json={
            "filename": FILE_NAME,
            "content_type": CONTENT_TYPE
        })
        req_response.raise_for_status()
        data = req_response.json()
        
        upload_url = data['upload_url']
        task_id = data['task_id']
        print(f"✔ Sucesso! Task ID: {task_id}")
        print(f"✔ URL S3 Gerada (assinada)")
    except Exception as e:
        print(f"❌ Erro ao solicitar upload: {e}")
        print(req_response.text)
        sys.exit(1)

    print(f"\n--- 2. Fazendo Upload direto para o S3 ---")
    try:
        with open(FILE_NAME, 'rb') as f:
            # Importante: Content-Type deve bater com o que foi assinado
            s3_response = requests.put(upload_url, data=f, headers={"Content-Type": CONTENT_TYPE})
            s3_response.raise_for_status()
        print("✔ Upload para o S3 concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro no upload para o S3: {e}")
        sys.exit(1)

    print(f"\n--- 3. Confirmando Upload na API ---")
    try:
        confirm_response = requests.post(f"{API_URL}/confirm-upload", json={
            "task_id": task_id
        })
        confirm_response.raise_for_status()
        print("✔ Confirmação aceita!")
        print(f"✔ Resposta Final: {confirm_response.json()}")
    except Exception as e:
        print(f"❌ Erro na confirmação: {e}")
        print(confirm_response.text)
        sys.exit(1)

if __name__ == "__main__":
    run_test()