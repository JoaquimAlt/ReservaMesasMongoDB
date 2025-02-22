from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from odmantic import ObjectId
from modelos import Mesa, Restaurante

router = APIRouter(
    prefix="/mesas",  # Prefixo para todas as rotas
    tags=["Mesas"],   # Tag para documentação automática
)

db = get_engine()

@router.get("/mesas/todas/", response_model=list[Mesa])
async def get_all_mesas() -> list[Mesa]:

    mesas = await db.find(Mesa)

    return mesas

@router.get("/mesas/buscar/{mesa_id}", response_model=list[Mesa])
async def get_mesa(mesa_id: str) -> list[Mesa]:

    mesas = await db.find(Mesa, Mesa.id == mesa_id)

    if not mesas:
        raise HTTPException(status_code = 404, detail= "Mesa não encontrado")
    
    return mesas


@router.post("/mesas/", response_model=Mesa)
async def post_mesa(mesa: Mesa) -> Mesa:

    buscar_restaurante = await db.find_one(Restaurante, Restaurante.id == mesa.restaurante.id)

    if buscar_restaurante:
        mesa.restaurante = buscar_restaurante

    mesa_final = await db.save(mesa)

    return mesa_final

@router.put("/mesas/{mesa_id}", response_model=Mesa)
async def update_mesa(mesa_id: str, mesa_data: dict) -> Mesa:
    
    mesa = await db.find_one(Mesa, Mesa.id == ObjectId(mesa_id))

    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrado")
    
    for key, value in mesa_data.items():
        setattr(mesa, key, value)

    await db.save(mesa)
    
    return mesa

@router.delete("/mesas/{mesa_id}", response_model=Mesa)
async def delete_mesa(mesa_id: str) -> Mesa:
    
    mesa = await db.find_one(Mesa, Mesa.id == ObjectId(mesa_id))

    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrado")
    
    return mesa

@router.get("/paginacao/", response_model=dict)
async def listar_mesas(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):

    pipeline = [
        {
            "$skip": skip
        },
        {
            "$limit": limit
        },
        {
            "$project": {
            "_id": 0,
            "restaurante": 0
            }
        }
    ]

    mesas = await db.get_collection(Mesa).aggregate(pipeline).to_list(length=limit)

    return {
        "Mesas": mesas
    }
