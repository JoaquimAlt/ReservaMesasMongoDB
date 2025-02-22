from odmantic import Model, Reference
from typing import Optional

class Usuario(Model):
    nome: str
    email: str
    telefone: Optional[str] = None

class Restaurante(Model):
    nome: str
    endereco: str
    telefone: Optional[str] = None

class Mesa(Model):
    numero: int
    cadeiras: int
    restaurante: Restaurante = Reference()

class Reserva(Model):
    usuario: Usuario = Reference()
    mesa: Mesa = Reference()
    horario: str

