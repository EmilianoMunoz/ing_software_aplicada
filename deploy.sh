# /bin/bash

IMAGE_NAME=flask_project
CONTAINER_NAME=flask_project
IMAGE_TAG=v1.0.0
RESOURCE_GROUP=umGroupResource
LOCATION=eastus
ACR_NAME=umingosftwareaplicada

az group create --name $RESOURCE_GROUP --location $LOCATION

az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
az acr login --name $ACR_NAME

ACR_REGISTRY_ID=$(az acr show --name $ACR_NAME --query id --output tsv)

SERVICE_PRINCIPAL_NAME=universidad

USER_NAME=$(az ad sp list --display-name $SERVICE_PRINCIPAL_NAME --query[app.Id --output tsv])
PASSWORD=$(az ad sp create-for-rbac --name $SERVICE_PRINCIPAL_NAME --scopes $ACR_REGISTRY_ID --role acrpull --query password --output tsv)

docker build -t $IMAGE_NAME:$IMAGE_TAG
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG
docker images
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG
az acr repository list --name $ACR_NAME --output table

az container create --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG --cpu 1 --memory 1
--registry-login-server $ACR_NAME.azurecr.io --ip-address Public --location $LOCATION --registry-username $USER_NAME --registry-password $PASSWORD 
--dns-name-label dns-um-$RANDOM --ports 5000