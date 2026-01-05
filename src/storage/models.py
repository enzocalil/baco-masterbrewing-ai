from pydantic import BaseModel, Field
from typing import List, Optional

class Ingredient(BaseModel):
    # Tornamos os campos técnicos opcionais para aceitar anotações incompletas
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = "N/A"
    step: Optional[str] = "N/A" 

class BeerRecipe(BaseModel):
    # O nome é o único campo obrigatório para catalogar
    name: str
    style: Optional[str] = "Estilo Desconhecido"
    
    # Parâmetros técnicos agora aceitam None se a IA não os encontrar
    target_og: Optional[float] = None
    target_fg: Optional[float] = None
    abv: Optional[float] = None
    ibu: Optional[int] = None
    
    # Listas vazias por padrão evitam erros de 'missing field'
    malts: List[Ingredient] = Field(default_factory=list)
    hops: List[Ingredient] = Field(default_factory=list)
    
    yeast: Optional[str] = "Levedura não especificada"
    sensory_profile: List[str] = Field(default_factory=list)
    description: Optional[str] = None