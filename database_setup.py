#!/usr/bin/env python2
# coding: utf-8

# Criação do banco de dados para o APP

from __future__ import absolute_import, unicode_literals
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Categories, Items, Users

engine = create_engine("sqlite:///catalog.db",
                       connect_args={"check_same_thread": False})
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Categorias que serão criadas no banco de dados
categories = ["TVs", "Smartphones", "Notebooks", "Games"]

results = session.query(Categories).all()
if not results:
    for c in categories:
        category = Categories(name=c)
        session.add(category)
    session.commit()
    print "Sessões Criadas"
else:
    print "Sessão já existente"

results = session.query(Categories).all()
print "\nCategories:\n"
for r in results:
    print "%s - %s" % (r.id, r.name)
