from fastapi import APIRouter, HTTPException
from database import get_engine
from odmantic import ObjectId
from modelos import Usuario

router = APIRouter(
    prefix="/usuarios",  # Prefixo para todas as rotas
    tags=["Usuarios"],   # Tag para documentação automática
)

db = get_engine();

@router.get("/usuarios/todos/", response_model=list[Usuario])
async def get_all_usuarios() -> list[Usuario]:
    
    usuarios = await db.find(Usuario)

    return usuarios

@router.get("/usuarios/buscar/{usuario_id}/", response_model=Usuario)
async def get_usuario(usuario_id: str) -> Usuario:

    usuario = await db.find_one(Usuario, Usuario.id == ObjectId(usuario_id))

    if not usuario:
        raise HTTPException(status_code = 404, detail= "Usuario não encontrado")
    
    return usuario


@router.post("/usuarios/", response_model=Usuario)
async def post_usuario(usuario: Usuario) -> Usuario:

    usuario = await db.save(usuario)

    return usuario

@router.put("/usuarios/{usuario_id}/", response_model=Usuario)
async def update_usuario(usuario_id: str, usuario_data: dict) -> Usuario:
    usuario = await db.find_one(Usuario, Usuario.id == ObjectId(usuario_id))

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    
    for key, value in usuario_data.items():
        setattr(usuario, key, value)

    await db.save(usuario)
    
    return usuario

@router.delete("/usuarios/{usuario_id}/", response_model=Usuario)
async def delete_usuario(usuario_id: str) -> Usuario:
    usuario = await db.find_one(Usuario, Usuario.id == ObjectId(usuario_id))

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    
    await db.delete(usuario) 
    
    return usuario

@router.get("/restaurantes/{usuario_nome}", response_model=list[dict])
async def buscar_usuarios(usuario_nome: str):
            
        pipeline = [
            {
                "$match": {
                    "nome": usuario_nome
                }
            },
            {
                "$lookup": {
                "from": "reserva",
                "localField": "_id",
                "foreignField": "usuario",
                "as": "reserva_info"
                }
            },
            {
                "$unwind": "$reserva_info"
            },
            {
                "$lookup": {
                "from": "mesa",
                "localField": "reserva_info.mesa",
                "foreignField": "_id",
                "as": "mesa_info"
                }
            },
            {
                "$unwind": "$mesa_info"
            },
            {
                "$lookup": {
                "from": "restaurante",
                "localField": "mesa_info.restaurante",
                "foreignField": "_id",
                "as": "restaurante_info"
                }
            },
            {
                "$unwind": "$restaurante_info"
            },
            {
                "$group": {
                "_id": "$restaurante_info.nome",
                "total_reservas": {"$sum": 1}
                }
            },
            {
                "$project": {
                "_id" : 0,
                "restaurante": "$_id",
                        "reservas_feitas": "$total_reservas"
                }
            }
        ]

        resultado = await db.get_collection(Usuario).aggregate(pipeline).to_list(None)

        return resultado