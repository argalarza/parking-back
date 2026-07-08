# Backend Endpoints Reales

Este mapa se genero leyendo `app/main.py`, routers, schemas Pydantic, casos de uso y repositorios del backend FastAPI. El frontend consume unicamente estas rutas reales.

## Autenticacion

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| POST | `/auth/admin/login` | JSON `{ "username": string, "password": string }` | `{ "access_token": string, "token_type": string, "must_change_password": boolean, "role": string }` | `Login.tsx` |
| POST | `/auth/login` | JSON `{ "email": string, "password": string }` | `{ "access_token": string, "token_type": string, "must_change_password": boolean }` | `Login.tsx` |
| POST | `/auth/change-password` | JSON `{ "current_password": string, "new_password": string }` con Bearer token de admin o persona | `{ "success": boolean, "message": string }` | `MySubscription.tsx` |

## Usuarios Administrativos

Todas las rutas requieren Bearer token de usuario administrativo con rol `admin` o `admin_ti`.

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| GET | `/admin/users` | Sin payload | `AdminUserResponse[]`: `{ "id": UUID, "username": string, "full_name": string \| null, "email": string \| null, "role": string, "is_active": boolean, "must_change_password": boolean, "created_date": datetime, "last_modified_date": datetime }[]` | No consumido en esta UI |
| GET | `/admin/users/{user_id}` | Path param `user_id` UUID | `AdminUserResponse` | No consumido en esta UI |
| POST | `/admin/users` | JSON `{ "username": string, "full_name": string, "email": string, "role": "admin" \| "admin_ti" \| "asesor" \| "operador" \| "supervisor" }` | `{ "success": boolean, "message": string, "id": UUID, "email_sent": boolean, "email_message": string }` | No consumido en esta UI |
| PATCH | `/admin/users/{user_id}/status` | Path param `user_id` UUID; JSON `{ "is_active": boolean }` | `{ "success": boolean, "message": string }` | No consumido en esta UI |

## Personas / Clientes

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| POST | `/gestion/persona` | JSON `{ "dni": string, "name": string, "last_names": string }` | `{ "success": boolean, "message": string, "id": UUID }` | No consumido en esta UI |

No existe endpoint real para listar, buscar, editar o eliminar personas/clientes.

## Visitantes

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| POST | `/visitantes/registro` | JSON `{ "first_names": string, "last_names": string, "dni_type": "CEDULA" \| "PASAPORTE", "dni": string, "phone": string, "email": string, "fingerprint_code": string \| null, "password": string }` | `{ "success": boolean, "person_id": UUID }` | No consumido en esta UI |

## Suscriptores / Suscripciones / Pagos

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| GET | `/suscripciones` | Sin payload. Requiere token administrativo con rol autorizado. | Lista de suscriptores con datos personales, ultimo pago, vigencia, estado y `subscription_active` | `Subscribers.tsx` |
| POST | `/suscripciones` | `multipart/form-data`: `first_names` string, `last_names` string, `email` string, `phone` string, `dni` string, `receipt` archivo PDF/JPG/PNG | `{ "success": boolean, "message": string, "person_id": UUID, "email_sent": boolean, "email_message": string }` | `Subscribers.tsx` |
| GET | `/suscripciones/me` | Sin payload. Requiere token de suscriptor. | `{ "id": UUID, "dni": string \| null, "first_names": string \| null, "last_names": string \| null, "email": string \| null, "phone": string \| null, "must_change_password": boolean, "amount": number \| null, "payment_date": date \| null, "valid_from": date \| null, "valid_until": date \| null, "status": string \| null, "is_active": boolean }` | `MySubscription.tsx` |

No existe endpoint real para descargar comprobantes ni validar pagos manualmente. El pago se crea validado automaticamente dentro de `POST /suscripciones`.

## Vehiculos

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| POST | `/gestion/vehiculo` | JSON `{ "plate": string, "brand": string, "model": string }` | `{ "success": boolean, "message": string, "id": UUID }` | No consumido en esta UI |
| POST | `/gestion/vincular` | JSON `{ "vehicle_id": UUID, "person_id": UUID, "relation": string }`; valores validos en caso de uso: `"DUENO"` o `"AUTORIZADO"` | `{ "success": boolean, "message": string }` | No consumido en esta UI |

No existe endpoint real para listar, buscar, editar o eliminar vehiculos.

## Puertas

Todas las rutas de puertas requieren Bearer token.

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| GET | `/puertas` | Sin payload | `GateResponse[]`: `{ "id": UUID, "number": number \| null, "main_street": string, "secondary_street": string \| null, "reference": string }[]` | No consumido en esta UI |
| GET | `/puertas/{gate_id}` | Path param `gate_id` UUID | `GateResponse` | No consumido en esta UI |
| POST | `/puertas` | JSON `{ "number": number \| null, "main_street": string, "secondary_street": string \| null, "reference": string }` | `{ "success": boolean, "message": string, "id": UUID \| null }` | No consumido en esta UI |
| PUT | `/puertas/{gate_id}` | Path param `gate_id` UUID; JSON `{ "number": number \| null, "main_street": string, "secondary_street": string \| null, "reference": string }` | `{ "success": boolean, "message": string, "id": UUID \| null }` | No consumido en esta UI |
| DELETE | `/puertas/{gate_id}` | Path param `gate_id` UUID | `{ "success": boolean, "message": string, "id": UUID \| null }` | No consumido en esta UI |

## Acceso Facial

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| POST | `/acceso/enrolar/{person_id}` | Path param `person_id` UUID; `multipart/form-data`: `file` imagen | `{ "success": boolean, "person_id": UUID }` | No consumido en esta UI |
| POST | `/acceso/verificar` | `multipart/form-data`: `gate_id` UUID, `file` imagen | Si autorizado: `{ "acceso": true, "mensaje": string, "persona": string, "vehiculo": string, "distancia": number }`; si no: `{ "acceso": false, "mensaje": string }` | No consumido en esta UI |

## Default

| Metodo | Endpoint | Payload esperado | Respuesta esperada | Componente frontend |
|---|---|---|---|---|
| GET | `/` | Sin payload | `{ "mensaje": string }` | No consumido en esta UI |
