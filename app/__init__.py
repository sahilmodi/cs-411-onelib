import os
import sqlalchemy
from yaml import load, Loader
from flask import Flask, jsonify
from pathlib import Path


app = Flask(__name__)
app.secret_key = "super secret key"

def init_connect_engine(gcloud=True):
    if not gcloud:
        pool = sqlalchemy.create_engine("mysql+pymysql://root:onelib@127.0.0.1:3306/onelib")
        return pool
    if os.environ.get("GAE_ENV") != "standard":
        variables = load(open("app.yaml"), Loader=Loader)
        env_variables = variables["env_variables"]
        for var in env_variables:
            os.environ[var] = env_variables[var]
        
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DB"),
            host=os.environ.get("MYSQL_HOST")
        )
    )
    return pool

db = init_connect_engine(gcloud=False)

from app import routes, user

# Change once we have a working login page
user.set_current_user_id(0)