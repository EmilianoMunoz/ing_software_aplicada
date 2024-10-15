import os
import subprocess as sp
from dotenv import load_dotenv

load_dotenv()

parameters = {
    "image_name": os.getenv("IMAGE_NAME"),
    "image_version": os.getenv("IMAGE_TAG"),
    "acr_name": os.getenv("ACR_NAME"),
    "resource_group": os.getenv("RESOURCE_GROUP"),
}

def run_command(command, error_message):
    """Ejecuta un comando en la terminal y maneja errores."""
    try:
        result = sp.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except sp.CalledProcessError as e:
        print(f"{error_message}: {e.stderr}")
        exit(1)

def create_or_update_acr():
    """Crea o actualiza el registro de contenedores de Azure si no existe."""
    print(f"Verificando si el registro de contenedores {parameters['acr_name']} existe...")
    
    try:
        result = sp.run(["az", "acr", "show", "--name", parameters["acr_name"], "--resource-group", parameters["resource_group"]], capture_output=True, text=True, check=True)
        print(f"Registro de contenedores {parameters['acr_name']} ya existe.")
    except sp.CalledProcessError:
        print(f"Registro de contenedores {parameters['acr_name']} no existe, creándolo...")
        run_command(
            ["az", "acr", "create", "--name", parameters["acr_name"], "--resource-group", parameters["resource_group"], "--sku", "Basic"], 
            f"Error al crear el registro de contenedores {parameters['acr_name']}"
        )

def create_or_update_resource_group():
    """Crea o actualiza el grupo de recursos si no existe."""
    print(f"Verificando si el grupo de recursos {parameters['resource_group']} existe...")
    
    try:
        result = sp.run(["az", "group", "show", "--name", parameters["resource_group"]], capture_output=True, text=True, check=True)
        print(f"Grupo de recursos {parameters['resource_group']} ya existe.")
    except sp.CalledProcessError:
        print(f"Grupo de recursos {parameters['resource_group']} no existe, creándolo...")
        run_command(
            ["az", "group", "create", "--name", parameters["resource_group"], "--location", "eastus"], 
            f"Error al crear el grupo de recursos {parameters['resource_group']}"
        )

def main():
    
    image_tag = f"{parameters['image_name']}:{parameters['image_version']}"
    print(f"Construyendo la imagen Docker: {image_tag}...")
    run_command(["docker", "build", "-t", image_tag, "."], "Error al construir la imagen Docker")

    create_or_update_resource_group()

    create_or_update_acr()

    print(f"Iniciando sesión en el registro de contenedores {parameters['acr_name']}...")
    run_command(["az", "acr", "login", "--name", parameters["acr_name"]], "Error al iniciar sesión en ACR")

    acr_image_tag = f"{parameters['acr_name']}.azurecr.io/{parameters['image_name']}:{parameters['image_version']}"

    print(f"Escaneando la imagen {image_tag} con Grype...")
    run_command(["grype", image_tag], "Error al escanear la imagen con Grype")

    print(f"Etiquetando la imagen como {acr_image_tag}...")
    run_command(["docker", "tag", image_tag, acr_image_tag], "Error al etiquetar la imagen Docker")

    print(f"Subiendo la imagen {acr_image_tag} al ACR...")
    run_command(["docker", "push", acr_image_tag], "Error al subir la imagen al ACR")

if __name__ == "__main__":
    main()
