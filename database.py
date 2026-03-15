from unittest.mock import Base
from sqlalchemy import Column, String, Float, ForeignKey 
from database import base
from pydantic import BaseModel 

class PedidoSchema(BaseModel):
    valor:float
    prestador_gateway_id: str

class SplitTransaction(Base):
    __tablename__ = "split_transacoes"

    tx_id = Column(String, primary_key=True, index=True)
    valor_total=Column(Float, nullable=False)
    valor_plataforma = Column(Float, nullable=False)
    valor_prestador = Column(Float, nullable=False)
    prestador_gateway_id = Column(String, nullable=False)
    status = Column(String, default="pendente")