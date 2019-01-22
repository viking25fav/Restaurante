#!/usr/bin/env python2
# coding: utf-8
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100, collation="NOCASE"), nullable=False)


class Items(Base):
    """
    O app não permite guardar items com o mesmo nome na mesma categoria visto
    que os endpoints utilizam os nomes dos mesmos. Por isso foi necessário a
    inclusão de uma Unique Constraint
    """
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("category_id", "title", name="un_title"),
    )

    id = Column(Integer, primary_key=True)
    # Atributo "collation" necessário para que o case dos nomes seja ignorado
    title = Column(String(100, collation="NOCASE"), nullable=False)
    description = Column(String(2000), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship(Categories)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(Users)


engine = create_engine("sqlite:///catalog.db",
                       connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
