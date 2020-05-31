#### Book Exchange Project


#### About 
This project being in its initial stage lets users exchange books from each other. User interested in the book will 
have to make a request to the owner of the book. Owner of the book will then either approve or reject the request.

#### Hosted on Heroku
http://read-meet-read.herokuapp.com/

#### Authorization
Authorisation has been setup using Auth0 as per the requirement, tokens have been added in .env for project evaluation. 


#### Roles & Permissions
1. Guest: Guest users can get list of users, a new user and approve users' request for a book. 
Guest user without token can access following endpoints ->  get: /users, post: /user, patch: /requests/user_id.

2. Reader: Users with this role can get list of books, add a book, get list of pending requests for a given user 
and also request a book from its owner. 
 
User with Reader role will have access to -> get: /books, post: /books, get:/requests/user_id, post: /requests/user_id

3. Admin: User with this role can delete a user -> DELETE /user/4



#### Getting Started
#### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

#### Running the application locally:

once project has been setup locally. execute below command to make environment variables available to the application.  

```bash
source .env
```

then, launch the application. 

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

#### Test endpoints using postman

Import Read-Meet-Read.postman_collection.json into Postman, tokens are there in the requests where necessary. 

For ease of testing, you can follow below approach. 

1. Get list of users - ####Two users have already been added. 
2. Add a user 
3. Get list of users 
4. delete new user
5. Get list of books - ####Three books have already been added. 
6. add a book
7. Get list of pending requests for a given user.
8. Request for a book from its owner. 
9. patch requests 


#### Test Cases

Before executing test cases, look out for 'TODOS' and change the user details accordingly.  

```bash
python3 test.py
```
