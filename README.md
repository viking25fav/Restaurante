# Udacity Desenvolvedor Web Full-Stack (Projeto 4) - Catálogo de Itens

Aplicativo que fornece uma lista de itens em uma variedade de categorias, bem como um sistema de registro e autenticação de usuários. Usuários registrados terão a capacidade de postar, editar e excluir seus próprios itens.


## Informações:

Aplicativo escrito em Python, desenvolvido utilizando o framework FLASK.

A autenticação é realizada por meio do API do Google.


## Instalação:

* Instale o [Vagrant](https://www.vagrantup.com/) e [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (necessários para executar a VM). 

* Acesse a pasta da VM e acesse a subpasta `vagrant`.

* Descompacte o arquivo Projeto4Flavio(v6);

* Execute os comandos abaixo para fazer a instalação e efetuar o login na VM (leva alguns minutos todo o processo)
    - `vagrant up`
    - `vagrant ssh`

* No terminal da VM crie o banco de dados:
    - `python database_setup.py`

* Inicialize o servidor:
    - `python server.py`

* Acesse a aplicação em seu navegador:
    - `http://localhost:8000`



## Copyright

Desenvolvido por Flavio André Virgilio
