import os.path
import uvicorn
from pony.orm import db_session, commit
from scheme import ProductsOut, ProducerOut, NewProducts, EditProducts, NewProducer, EditProducer, CoolLvL
from scheme import UserInDB, UserOut, UserEntr
from models import db, Producer, Products, User
from s_main import *
from s_scheme import *
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Body, Depends, status, HTTPException

# использовать exception
# TODO: add hashed_password -> password

app = FastAPI()
my_db = 'Manufacturer_and_Products.sqlite'


@app.on_event("startup")
async def start_app():
    """Выполняется при старте приложения"""
    # Прежде чем мы сможем сопоставить сущности с базой данных,
    # нам нужно подключиться, чтобы установить соединение с ней.
    # Это можно сделать с помощью метода bind()
    create_db = True
    if os.path.isfile(my_db):
        create_db = False
    db.bind(provider='sqlite', filename=my_db, create_db=create_db)
    db.generate_mapping(create_tables=create_db)


@app.post('/api/user/new', tags=['user'])
async def new_user(user: UserEntr = Body(...)):
    with db_session:
        n_user = user.dict()

        if User.exists(id=user.id):
            return 'пользователь с таким id уже существует'

        if User.exists(username=user.username):
            return 'пользователь с таким именем уже существует'

        password = n_user['hashed_password']
        n_user['hashed_password'] = get_password_hash(password)

        User(**n_user)
        commit()
        return UserOut.from_orm(user)


@app.get('/api/user', tags=['user'])
async def get_all_users():
    with db_session:
        users = User.select()  # преобразуем запрос в SQL, а затем отправим в базу данных
        all_users = []
        for i in users:
            all_users.append(UserOut.from_orm(i))
    return all_users


@app.get("/users/me/", response_model=UserOut, tags=['user'])
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/", tags=['user'])
async def read_own_items(current_user: UserInDB = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


# -----------------------------------------------------------------------------------------
'''
@app.post("/token", response_model=Token, tags=['token'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)  # UserInDB or False
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 30 min
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}'''
try:
    @app.post("/token", response_model=Token, tags=['token'])
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(form_data.username, form_data.password)  # UserInDB or False
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 30 min
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
except Exception:
    'ошибка'
# -----------------------------------------------------------------------------------------


@app.get('/api/products', tags=['products'])
async def get_all_products():
    with db_session:
        products = Products.select()  # преобразуем запрос в SQL, а затем отправим в базу данных
        all_products = []
        for i in products:
            all_products.append(ProductsOut.from_orm(i))
    return all_products


@app.get('/api/product/get_average_products', tags=['products'])
async def get_average(minimum: int, maximum: int):
    with db_session:
        products = Products.select(lambda p: (minimum <= p.price) and (p.price <= maximum))[::]  # работает
        all_products = []
        for i in products:
            all_products.append(ProductsOut.from_orm(i))
        return all_products


@app.get('/api/product/{item_id}', tags=['products'])
async def get_product(item_id: int):
    with db_session:
        if Products.exists(id=item_id):
            product = Products.get(id=item_id)
            return ProductsOut.from_orm(product)
        else:
            return 'товара с таким id не существует'


@app.post('/api/product/new', tags=['products'])
async def new_product(n_product: NewProducts = Body(...), current_user: UserInDB = Depends(get_current_active_user)):
    with db_session:

        product = n_product.dict()

        if Products.exists(id=int(n_product.id)):
            return 'товар с таким id уже существует'

        if not Producer.exists(id=int(n_product.producer)):
            return 'Производителя с таким id не существует'

        Products(**product)
        commit()
        return n_product


@app.put('/api/product/edit/{item_id}', tags=['products'])
async def edit_product(item_id: int, edit_pr: EditProducts = Body(...),
                       current_user: UserInDB = Depends(get_current_active_user)):
    with db_session:
        if Products.exists(id=item_id):
            product = edit_pr.dict(exclude_unset=True, exclude_none=True)
            Products[item_id].set(**product)
            if not Producer.exists(id=edit_pr.producer):
                if edit_pr.producer != None:
                    return 'Производителя с таким id не существует'
            commit()
            return ProductsOut.from_orm(Products[item_id])
        return 'товара с таким id не существует'


@app.delete('/api/product/delete/{item_id}', tags=['products'])
async def delete_product(item_id: int, current_user: UserInDB = Depends(get_current_active_user)):
    with db_session:
        if Products.exists(id=item_id):
            Products[item_id].delete()
            commit()
            return "Объект удалён"
        return "производителя с таким id не существует"


# ----------------------------------------------------------------------------------------


@app.get('/api/producer/get_cool_producers', tags=['producers'])
async def get_cool(cool_level: int):
    with db_session:
        producer = Producer.select(lambda p: len(p.products) >= cool_level)[::]  # работает
        all_producer = []
        for i in producer:
            all_producer.append(CoolLvL.from_orm(i))
        return all_producer


@app.get('/api/producers', tags=['producers'])
async def get_all_producers():
    with db_session:
        producer = Producer.select()[:]  # преобразуем запрос в SQL, а затем отправим в базу данных
        all_producer = []
        for i in producer:
            all_producer.append(ProducerOut.from_orm(i))
    return all_producer


@app.get('/api/producer/{item_id}', tags=['producers'])
async def get_producer(item_id: int):
    with db_session:
        if Producer.exists(id=item_id):
            producer = Producer.get(id=item_id)
            return ProducerOut.from_orm(producer)
        else:
            return 'товара с таким id не существует'


@app.post('/api/producer/new', tags=['producers'])
async def new_producer(n_producer: NewProducer = Body(...)):
    with db_session:
        producer = n_producer.dict()

        if Producer.exists(id=int(n_producer.id)):
            return 'производитель с таким id уже существует'

        producer = Producer(**producer)
        commit()
        return ProducerOut.from_orm(producer)


@app.put('/api/producer/edit/{item_id}', tags=['producers'])
async def edit_producer(item_id: int, edit_pr: EditProducer = Body(...)):
    with db_session:
        if Producer.exists(id=item_id):
            producer = edit_pr.dict(exclude_unset=True, exclude_none=True)
            Producer[item_id].set(**producer)
            commit()
            return ProducerOut.from_orm(Producer[item_id])
        return 'производителя с таким id не существует'


@app.delete('/api/producer/delete/{item_id}', tags=['producers'])
async def delete_producer(item_id: int):
    with db_session:
        if Producer.exists(id=item_id):
            Producer[item_id].delete()
            commit()
            return "Объект удалён"
        return "производителя с таким id не существует"


@app.get('/api/producer/{item_id}/products', tags=['producers'])
async def sorted_products(item_id: int):
    with db_session:
        if Producer.exists(id=item_id):
            producer = Producer.get(id=item_id)
            pr = producer.products.select().order_by(Products.price)[::]
            return ProducerOut(**(producer.to_dict() | {'products': pr}))
        return 'Производителя с таким id не существует'


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
