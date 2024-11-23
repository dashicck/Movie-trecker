from sqlalchemy import Column, Integer, String, Float
from database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rating = Column(Float, nullable=True)  #Оценка
    comment = Column(String, nullable=True)  #Комментарий
    watched_status = Column(String, default="Not Watched")  # Статус просмотра
