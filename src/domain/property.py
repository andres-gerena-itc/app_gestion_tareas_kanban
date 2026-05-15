from enum import Enum
from typing import Any, Dict, Optional

class PropertyType(Enum):
    STATUS = "Status"
    SELECT = "Select"
    MULTI_SELECT = "MultiSelect"
    DATE = "Date"
    FORMULA = "Formula"
    RELATION = "Relation"

class PropertySchema:
    """
    Define la estructura y validación de una propiedad dinámica en un Workspace.
    """
    def __init__(self, name: str, type: PropertyType, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.type = type
        self.config = config if config is not None else {}

    def validate(self, value: Any) -> bool:
        """
        Valida que un valor concreto cumpla con este esquema (INV-06).
        Lanza InvalidPropertyValueError si la validación falla.
        """
        from .exceptions import InvalidPropertyValueError
        
        if value is None:
            return True # Permitimos limpieza de valores

        try:
            if self.type == PropertyType.STATUS or self.type == PropertyType.SELECT:
                options = self.config.get("options", [])
                if value not in options:
                    raise InvalidPropertyValueError(f"Valor '{value}' no está en las opciones permitidas: {options}")
            
            elif self.type == PropertyType.MULTI_SELECT:
                if not isinstance(value, list):
                    raise InvalidPropertyValueError("MultiSelect requiere una lista de valores.")
                options = self.config.get("options", [])
                for val in value:
                    if val not in options:
                        raise InvalidPropertyValueError(f"Valor '{val}' no está en las opciones permitidas: {options}")
            
            elif self.type == PropertyType.DATE:
                if not isinstance(value, str):
                    raise InvalidPropertyValueError("Date requiere un string (ISO-8601).")
                
            elif self.type == PropertyType.RELATION:
                if not isinstance(value, str):
                    raise InvalidPropertyValueError("Relation requiere un ID en string.")
                    
        except InvalidPropertyValueError:
            raise
        except Exception as e:
            raise InvalidPropertyValueError(f"Error de validación inesperado: {e}")
            
        return True
