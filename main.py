from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import database
import httpx


app = FastAPI()

#Создание базы данных
models.Base.metadata.create_all(bind=database.engine)

#Зависимость для работы с БД
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Маршрут для получения всех фильмов
@app.get("/movies/", response_model=list[schemas.Movie])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies

#Маршрут для добавления нового фильма
@app.post("/movies/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

#Маршрут для обновления фильма
@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

#Маршрут для удаления фильма
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(db_movie)
    db.commit()
    return {"detail": "Movie deleted successfully"}

#Новый маршрут для получения информации о фильме из OMDb API
OMDB_API_KEY = "46cebc75"  # Вставь сюда свой ключ
OMDB_API_URL = "http://www.omdbapi.com/"

@app.get("/movies/{title}")
async def get_movie_info(title: str):
    """
    Получает информацию о фильме по его названию.
    """
    params = {
        "apikey": OMDB_API_KEY,
        "t": title
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(OMDB_API_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при запросе к внешнему API")
        data = response.json()
        if data.get("Response") == "False":
            raise HTTPException(status_code=404, detail=data.get("Error", "Фильм не найден"))
        return data
    
    #Маршрут для добавления фильма из OMDb API в локальную базу
@app.post("/movies/from-omdb/", response_model=schemas.Movie)
async def add_movie_from_omdb(title: str, db: Session = Depends(get_db)):
    """
    Получает информацию о фильме из OMDb API и добавляет его в локальную базу данных.
    """
    OMDB_API_KEY = "46cebc75" 
    OMDB_API_URL = "http://www.omdbapi.com/"

    params = {
        "apikey": OMDB_API_KEY,
        "t": title
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(OMDB_API_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при запросе к OMDb API")
        data = response.json()
        if data.get("Response") == "False":
            raise HTTPException(status_code=404, detail=data.get("Error", "Фильм не найден"))

    #Извлечение данных из ответа OMDb API
    movie_data = {
        "title": data.get("Title"),
        "year": data.get("Year"),
        "genre": data.get("Genre")
    }

    #Создание объекта фильма в локальной базе данных
    db_movie = models.Movie(**movie_data)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie
#uvicorn main:app --reload

