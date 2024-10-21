from pydantic import BaseModel, Field
from typing import Optional

class ProductMessage(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_family: Optional[str] = None
    product_group: Optional[str] = None
    product_offer_price: Optional[str] = None
    pop_type: Optional[str] = None
    price_category: Optional[str] = None
    price_mode: Optional[str] = None
    product_specification_type: Optional[str] = None
    data_allowance: Optional[str] = None
    voice_allowance: Optional[str] = None

class ProductSchema(BaseModel):
    price: int = Field(0, example=10)
    validity: int = Field(0, example=30)
    validity_time_period: str = Field("string", example="days")
    daily_limit: str = Field("string", example="N/A")
    voice_unit: str = Field("string", example="N/A")
    voice_unit_value: str = Field("string", example="N/A")
    data_unit_value: str = Field("string", example="1")
    data_unit: str = Field("string", example="GB")