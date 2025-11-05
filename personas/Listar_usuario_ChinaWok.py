import boto3
import os
import json

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")
TOKEN_FUNCTION_NAME = "Validar_Token_Acceso_ChinaWok"

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)

def _get_token(event):
    headers = event.get("headers", {}) or {}
    auth = headers.get("Authorization") or headers.get("authorization")
    if not auth:
        return None
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return auth

def _validar_token(token):
    payload = {"token": token}
    invoke_response = lambda_client.invoke(
        FunctionName=TOKEN_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8")
    )
    return json.loads(invoke_response["Payload"].read())

def lambda_handler(event, context):
    token = _get_token(event)
    if not token:
        return {"statusCode": 401, "body": {"message": "Falta token"}}

    resp_val = _validar_token(token)
    if resp_val.get("statusCode") != 200:
        return {"statusCode": 403, "body": {"message": "Acceso no autorizado"}}

    role = resp_val.get("body", {}).get("role", "Cliente")
    if role.lower() != "admin":
        return {"statusCode": 403, "body": {"message": "Solo los administradores pueden listar usuarios"}}

    resp = usuarios_table.scan()
    items = resp.get("Items", [])
    for u in items:
        u.pop("contrasena", None)

    return {
        "statusCode": 200,
        "body": {"total": len(items), "usuarios": items}
    }
