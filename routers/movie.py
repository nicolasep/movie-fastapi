from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.security import HTTPBearer
from bd.database import Session, engine, Base 
from models.movies import Movie as ModielMovie
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter
from user_jwt import createToken, validateToken

routerMovie = APIRouter()


movies = [     
    {
        "id": 1,
        "title": "Inception",
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "year": 2010,
        "rating": 8.8,
        "category": "Sci-Fi"
    },
    {
        "id": 2,
        "title": "The Shawshank Redemption",
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "year": 1994,
        "rating": 9.3,
        "category": "Drama"
    },
    {
        "id": 3,
        "title": "The Godfather",
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "year": 1972,
        "rating": 9.2,
        "category": "Crime"
    },
    {
        "id": 4,
        "title": "The Dark Knight",
        "overview": "When the menace known as the Joker emerges from his mysterious past, he wreaks havoc and chaos on the people of Gotham.",
        "year": 2008,
        "rating": 9.0,
        "category": "Action"
    },
    {
        "id": 5,
        "title": "Pulp Fiction",
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "year": 1994,
        "rating": 8.9,
        "category": "Crime"
    } 
]

class BearerJWT(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data= validateToken(auth.credentials)
        if data['email'] != 'nicolas':
            raise HTTPException(status_code=403, detail='Credenciales incorrectas')
        
class Movie(BaseModel):
    id: Optional [int] = None
    title: str = Field(default='Titulo de la pelicula',min_lengh=5, max_lengh=60)
    overview: str = Field(default='Descripcion de la pelicula',min_lengh=5, max_lengh=60)
    year: int = Field(default=2023)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_lengh=3, max_lengh=15,default='Aqui va la categoria')

    
@routerMovie.get('/Movies', tags=['Movies'], dependencies=[Depends(BearerJWT())])
def get_movies():
    db = Session()
    data= db.query(ModielMovie).all()
    return JSONResponse(content=jsonable_encoder(data)) #movies

@routerMovie.get('/Movies/{id}',tags=['Movies'])
def get_movie(id: int = Path(ge=1, le=100)):
    db = Session()
    data= db.query(ModielMovie).filter(ModielMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'messag':'Recurso no encontrado'})
    return JSONResponse(status_code=200, content=jsonable_encoder(data))

@routerMovie.get('/Movies/', tags=['Movies'])
def get_movies_by_category(category: str = Query(min_lengh=3, max_lengh=15)):
    db = Session()
    data= db.query(ModielMovie).filter(ModielMovie.category == category).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(data))

@routerMovie.post('/Movies', tags=['Movies'], status_code=201)
def create_movie(movie: Movie):
    db = Session()
    newMovie = ModielMovie(**movie.dict())
    db.add(newMovie)
    db.commit()
    return JSONResponse(content={'message':'Se ha cargado una nueva pelicula'})

@routerMovie.put('/Movies{id}', tags=['Movies'])
def update_movie(id: int, movie:Movie):
    db = Session()
    data = db.query(ModielMovie).filter(ModielMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'messag':'Recurso no encontrado'})

    data.title = movie.title
    data.overview = movie.overview
    data.year = movie.year
    data.rating = movie.rating
    data.category = movie.category
    db.commit()
    return JSONResponse(content={'message':'Se ha modificado la pelicula'})
    
@routerMovie.delete('/Movies{id}', tags=['Movies'])
def delete_movie(id:int):
    db = Session()
    data = db.query(ModielMovie).filter(ModielMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'messag':'Recurso no encontrado'})
    db.delete(data)
    db.commit()
    return JSONResponse(content={'message':'Se ha eliminado la pelicula','data':jsonable_encoder(data)})