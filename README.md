# 🧩 API CRUD de Usuarios – ChinaWok (AWS Lambda + DynamoDB)

Este proyecto implementa un CRUD completo de usuarios utilizando AWS Lambda, API Gateway y DynamoDB, gestionado mediante el framework Serverless. Incluye autenticación con tokens temporales, control de roles (Cliente / Admin) y endpoints protegidos. Se utiliza Python 3.12, AWS Lambda, AWS API Gateway, AWS DynamoDB, Serverless Framework y Postman para pruebas. La estructura del proyecto es: crud-usuarios/ ├── crear_usuario.py ├── login.py ├── listar_usuarios.py ├── buscar_usuario.py ├── modificar_usuario.py ├── eliminar_usuario.py ├── validar_token.py ├── requirements.txt └── serverless.yml. Para desplegarlo se ejecuta: npm install -g serverless, pip install -r requirements.txt, aws configure y serverless deploy, lo que crea automáticamente los endpoints en API Gateway.

Los endpoints disponibles son: Crear usuario (POST /usuario/crear) sin token, público; Login (POST /usuario/login) sin token, público; Listar usuarios (GET /usuario/listar) con token, solo Admin; Buscar usuario (POST /usuario/buscar) con token, solo Admin; Modificar usuario (PUT /usuario/modificar) con token, permitido para Cliente o Admin; Eliminar usuario (DELETE /usuario/eliminar) con token, solo Admin; Validar token (POST /usuario/validartoken) con token, accesible para todos. 

Cada usuario se almacena en DynamoDB con el esquema: { "nombre": "string", "correo": "string", "contrasena": "string", "role": "Cliente | Admin", "informacion_bancaria": { "numero_tarjeta": "string", "cvv": "string", "fecha_vencimiento": "string", "direccion_facturacion": "string" } }. Por defecto, los usuarios nuevos se crean con rol Cliente. Los Admins pueden listar, buscar o eliminar usuarios, mientras que los Clientes solo pueden modificar su información o tarjeta.

El login genera un token UUID con duración de 60 minutos, almacenado en la tabla ChinaWok-Tokens. Todas las funciones protegidas invocan la Lambda Validar_Token_Acceso_ChinaWok para comprobar validez. El token incluye correo y rol del usuario, lo que permite al frontend conocer permisos sin pedir datos adicionales.

Para pruebas, se incluye la colección Postman “Chinawok - Usuarios con Token Admin.postman_collection.json” con logins preconfigurados (Cliente y Admin), almacenamiento automático de {{token}} y {{token_admin}}, y rutas con autorización Bearer configuradas. 

Roles y seguridad: Cliente puede modificar su información personal o bancaria. Admin puede listar, buscar, eliminar usuarios y cambiar roles. Para crear un Admin: (1) crear un usuario como Cliente, (2) iniciar sesión como Admin y (3) modificar su rol a Admin desde el endpoint /usuario/modificar o directamente en DynamoDB.

Ejemplo creación usuario: POST /usuario/crear { "nombre": "Usuario Prueba", "correo": "cliente@chinawok.pe", "contrasena": "Cliente123!" }. Ejemplo actualización de tarjeta: PUT /usuario/modificar { "correo": "cliente@chinawok.pe", "informacion_bancaria": { "numero_tarjeta": "4111111111111111", "cvv": "123", "fecha_vencimiento": "12/25", "direccion_facturacion": "Lima, Perú" } }.

Autor: Corporación Larfarma / ChinaWok – División de Desarrollo Backend. Desarrollado en AWS Lambda (Python). Versión estable: Noviembre 2025.
