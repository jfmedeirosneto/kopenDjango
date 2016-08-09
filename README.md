# kopenDjango

Social network to share sales promotions
Rede social para compartilhar ofertas

Copyright(c) 2016 João Neto <<jfmedeirosneto@yahoo.com.br>>

## Recursos

- Front-end desenvolvido em jQuery Mobile e HTML5
- Back-end desenvolvido em Python 2.7.12 com framework Django 1.5
- Integração com banco de dados para armazenar ofertas
- Página de entrada com ofertas em destaque
- Busca de ofertas pelo nome do produto
- Cadastro de novas ofertas
- Cadastro de usuário via email ou Facebook
- Compartilhamento de ofertas em redes sociais
- Botões para classificar a oferta
- Botão para informar erro em oferta
- Sistema de promoção de ofertas patrocinadas
- Sistema de pontuação para usuário em função da sua interação
- Página de ranking de usuários em função da pontuação
- Página de contato com adminstrador do sistema
- Página de termos de uso do sistema

## Utilização kopenDjango

A aplicação kopenDjango foi utilizado no site ofertasQui.com.br em 2013 para divulgar ofertas das cidades de Jaraguá do Sul e Guaramirim

Hoje o site ofertasQui.com.br encontra-se desativado

## Screenshots site ofertasQui.com.br

### Página de entrada

![Página de Entrada](https://raw.githubusercontent.com/jfmedeirosneto/kopendjango/master/screenshots/main-page.png "Página de entrada")

### Adicionar nova oferta

![Adicionar nova oferta](https://raw.githubusercontent.com/jfmedeirosneto/kopendjango/master/screenshots/add-sale-page.png "Adicionar nova oferta")

### Oferta

![Oferta](https://raw.githubusercontent.com/jfmedeirosneto/kopendjango/master/screenshots/sale-page.png "Oferta")

### Divulgação ofertasQui.com.br

![Divulgação ofertasQui.com.br](https://raw.githubusercontent.com/jfmedeirosneto/kopendjango/master/screenshots/ofertas-qui.png "Divulgação ofertasQui.com.br")

## Executar kopenDjango

Clone ou faça o download do kopenDjango em seu computador

Instalar Python 2.7.12

[www.python.org](https://www.python.org/ "Python")

Abrir command prompt no diretório do kopenDjango

Instalar Django 1.5

``` bash
easy_install.exe django==1.5
```
	
Instalar Pillow

``` bash
easy_install.exe pillow
```

Sincronizar base de dados

``` bash
python manage.py syncdb
```

Executar servidor

``` bash
python manage.py runserver
```

Abrir o navegador web no endereço http://127.0.0.1:8000

## Licença

GNU GPLv3