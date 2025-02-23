from fastapi import APIRouter, HTTPException
from database import get_engine
from odmantic import ObjectId
from modelos import Mesa, Reserva, Restaurante, Usuario

router = APIRouter(
    prefix="/Reservas",  # Prefixo para todas as rotas
    tags=["Reservas"],   # Tag para documentação automática
)

db = get_engine();

@router.get("/reservas/todas/", response_model=list[Reserva])
async def get_all_reservas(mes: str = None) -> list[Reserva]:
    reservas = await db.find(Reserva)

    if mes:
        reservas = [reserva for reserva in reservas if reserva.horario[3:5] == mes]

    return reservas


@router.get("/reservas/buscar/{reserva_id}/", response_model=Reserva)
async def get_reserva(reserva_id: str) -> Reserva:

    reserva = await db.find_one(Reserva, Reserva.id == ObjectId(reserva_id))

    if not reserva:
        raise HTTPException(status_code = 404, detail= "Reserva não encontrado")
    
    return reserva


@router.post("/reservas/", response_model=Reserva)
async def post_reserva(reserva: Reserva) -> Reserva:

    buscar_usuario = await db.find_one(Usuario, Usuario.id == reserva.usuario.id)

    if buscar_usuario:
        reserva.usuario = buscar_usuario

    buscar_mesa = await db.find_one(Mesa, Mesa.id == reserva.mesa.id)

    if buscar_mesa:
        reserva.mesa = buscar_mesa

    reserva_final = await db.save(reserva)

    return reserva_final

@router.put("/reservas/{reserva_id}/", response_model=Reserva)
async def update_reserva(reserva_id: str, reserva_data: dict) -> Reserva:
    reserva = await db.find_one(Reserva, Reserva.id == ObjectId(reserva_id))

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrado")
    
    for key, value in reserva_data.items():
        setattr(reserva, key, value)

    await db.save(reserva)
    
    return reserva

@router.delete("/reservas/{reserva_id}/", response_model=Reserva)
async def delete_reserva(reserva_id: str) -> Reserva:
    reserva = await db.find_one(Reserva, Reserva.id == ObjectId(reserva_id))

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrado")
    
    await db.delete(reserva) 
    
    return reserva

@router.get("/clientes/{usuario_nome}", response_model=list[dict])
async def reservas_do_cliente(usuario_nome: str):
    pipeline = [
        {
            "$match": {
                "nome": {"$regex": usuario_nome, "$options": "i"}
            }
        },
        {
            "$lookup": {
                "from": "reserva",
                "localField": "_id",
                "foreignField": "usuario",
                "as": "reservas"
            }
        },
        {
            "$unwind": "$reservas"
        },
        {
            "$lookup": {
                "from": "mesa",
                "localField": "reservas.mesa",
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
            "$project": {
                "_id": 0,
                "usuario": "$nome",
                "mesa": "$mesa_info.numero",
                "horario": "$reservas.horario",
                "restaurante": "$restaurante_info.nome"
            }
        }
    ]

    resultado = await db.get_collection(Usuario).aggregate(pipeline).to_list(None)

    return resultado