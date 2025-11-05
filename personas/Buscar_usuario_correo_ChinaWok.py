import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")
TOKEN_FUNCTION_NAME = os.getenv("TOKEN_FUNCTION_NAME", "Validar_Token_Acceso_ChinaWok")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)

def _parse_body(event):
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body) if body.strip() else {}
    elif not isinstance(body, dict):
        body = {}
    return body

def _get_token(event, body):
    headers = event.get("headers", {}) or {}
    token = headers.get("Authorization") or headers.get("authorization") or body.get("token")
    if not token:
        return None
    if isinstance(token, str) and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()
    return token

def _validar_token(token):
    payload = {"token": token}
    invoke_response = lambda_client.invoke(
        FunctionName=TOKEN_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8")
    )
    return json.loads(invoke_response["Payload"].read())

def lambda_handler(event, context):
    body = _parse_body(event)
    token = _get_token(event, body)
    if not token:
        return {"statusCode": 401, "body": {"message": "Falta token"}}

    resp_val = _validar_token(token)
    if resp_val.get("statusCode") != 200:
        return {"statusCode": 403, "body": {"message": "Acceso no autorizado"}}

    role = resp_val.get("body", {}).get("role", "Cliente")
    if role.lower() != "admin":
        return {"statusCode": 403, "body": {"message": "Solo los administradores pueden buscar usuarios"}}

    path_params = event.get("pathParameters") or {}
    correo = path_params.get("correo") or body.get("correo") or event.get("correo")
    if not correo:
        return {"statusCode": 400, "body": {"message": "correo es obligatorio"}}

    resp = usuarios_table.get_item(Key={"correo": correo})
    if "Item" not in resp:
        return {"statusCode": 404, "body": {"message": "Usuario no encontrado"}}

    user = resp["Item"]
    user.pop("contrasena", None)

    full_user = {
        "nombre": user.get("nombre"),
        "correo": user.get("correo"),
        "role": user.get("role"),
        "informacion_bancaria": {
            "numero_tarjeta": None,
            "cvv": None,
            "fecha_vencimiento": None,
            "direccion_facturacion": None
        }
    }

    if "informacion_bancaria" in user:
        info = user["informacion_bancaria"]
        full_user["informacion_bancaria"]["numero_tarjeta"] = info.get("numero_tarjeta")
        full_user["informacion_bancaria"]["cvv"] = info.get("cvv")
        full_user["informacion_bancaria"]["fecha_vencimiento"] = info.get("fecha_vencimiento")
        full_user["informacion_bancaria"]["direccion_facturacion"] = info.get("direccion_facturacion")

    return {"statusCode": 200, "body": full_user}
