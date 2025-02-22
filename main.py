from fastapi import FastAPI
from rotas import usuario, mesa, restaurante, reserva
# FastAPI app instance
app = FastAPI()
# Rotas para Endpoints
app.include_router(reserva.router)
app.include_router(usuario.router)
app.include_router(mesa.router)
app.include_router(restaurante.router)

