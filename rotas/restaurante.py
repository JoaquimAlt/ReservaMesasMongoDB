from typing import Collection
from fastapi import APIRouter, HTTPException
from database import get_engine
from odmantic import ObjectId
from modelos import Mesa, Restaurante

router = APIRouter(
    prefix="/restaurantes",  # Prefixo para todas as rotas
    tags=["Restaurante"],   # Tag para documentação automática
)

db = get_engine()

@router.get("/restaurantes/todos/", response_model=list[Restaurante])
async def get_all_restaurantes() -> list[Restaurante]:

    restaurantes = await db.find(Restaurante)

    return restaurantes

@router.get("/restaurantes/buscar/{restaurante_nome}", response_model=list[Restaurante])
async def get_restaurante(restaurante_nome: str) -> list[Restaurante]:

    restaurantes = await db.find(Restaurante, Restaurante.nome == restaurante_nome)

    if not restaurantes:
        raise HTTPException(status_code = 404, detail= "Restaurante não encontrado")
    
    return restaurantes


@router.post("/restaurantes/", response_model=Restaurante)
async def inserir_restaurante(restaurante: Restaurante) -> Restaurante:

    restaurante = await db.save(restaurante)

    return restaurante

@router.put("/restaurantes/{restaurante_id}", response_model=Restaurante)
async def atualizar_restaurante(restaurante_id: str, restaurante_data: dict) -> Restaurante:
    
    restaurante = await db.find_one(Restaurante, Restaurante.id == ObjectId(restaurante_id))

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    for key, value in restaurante_data.items():
        setattr(restaurante, key, value)

    await db.save(restaurante)
    
    return restaurante

@router.delete("/restaurantes/{restaurante_id}", response_model=Restaurante)
async def deletar_restaurante(restaurante_id: str) -> Restaurante:
    
    restaurante = await db.find_one(Restaurante, Restaurante.id == ObjectId(restaurante_id))

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    return restaurante

@router.get("/mesas/{restaurante_nome}", response_model=dict)
async def listar_mesas_restaurante(restaurante_nome: str) -> list[Mesa]:

    restaurante = await db.find_one(Restaurante, Restaurante.nome == restaurante_nome)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    mesas_cursor = db.get_collection(Mesa).find(
        {"restaurante": restaurante.id},
        {"_id": 0, "restaurante": 0}
    ).sort("numero", 1)  

    quantidade_mesas = await db.get_collection(Mesa).count_documents({"restaurante": restaurante.id})

    mesas = await mesas_cursor.to_list(None)

    return {
        "restaurante": restaurante.nome,
        "quantidade de mesas do restaurante": quantidade_mesas,
        "mesas": mesas
    }


