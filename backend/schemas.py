from pydantic import BaseModel, Field

class AlertCreate(BaseModel):
    product_id: int
    target_price: float = Field(gt=0)
