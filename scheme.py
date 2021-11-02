from typing import Optional
from pydantic import BaseModel, validator


#  Чтобы в полной мере использовать FastAPI,
#  модели Пони должны работать со схемами pydantic


class ProducerOutForProducts(BaseModel):
    id: int
    name: str
    country: str


class ProductsOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    producer: ProducerOutForProducts

    @validator('producer', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, value):  # Добавляет всю инфу о продуктах
        if hasattr(value, "to_dict"):
            value = value.to_dict()
        return value

    class Config:
        orm_mode = True


class ProductOutForProducer(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]

    class Config:
        orm_mode = True


class ProducerOut(BaseModel):
    id: int
    name: str
    country: str
    products: list[ProductOutForProducer]

    @validator('products', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        new_values = list()  # Добавляет всю инфу о продуктах
        for v in values:
            if hasattr(v, "to_dict"):
                new_values.append(v.to_dict())
        return new_values

    class Config:
        orm_mode = True


class NewProducts(BaseModel):
    id: int
    name: str
    price: float
    description: str
    producer: int


class EditProducts(BaseModel):
    name: Optional[str]
    price: Optional[float]
    description: Optional[str]
    producer: Optional[int]


class CoolLvL(BaseModel):
    id: int
    name: str
    country: str

    class Config:
        orm_mode = True


class NewProducer(BaseModel):
    id: int
    name: str
    country: str

    class Config:
        orm_mode = True


class EditProducer(BaseModel):
    name: Optional[str]
    country: Optional[str]


class SortedProductsForProducer(BaseModel):
    products: list[ProductOutForProducer]

    @validator('products', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        new_values = list()  # Добавляет всю инфу о продуктах
        for v in values:
            if hasattr(v, "to_dict"):
                new_values.append(v.to_dict())
        return new_values

    class Config:
        orm_mode = True

'''
class UserEntr(BaseModel):
    id: int
    username: str
    full_name: str
    hashed_password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True


class UserInDB(UserOut):
    hashed_password: str
'''