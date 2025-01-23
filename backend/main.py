# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
import os

from flask import Flask, request, jsonify

import sqlalchemy

USERS = "users"

from connect_connector import connect_with_connector

ERROR_NOT_FOUND = {'Error' : 'Not Found'}

app = Flask(__name__)

logger = logging.getLogger()

# Sets up connection pool for the app
def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    if os.environ.get('INSTANCE_CONNECTION_NAME'):
        return connect_with_connector()

    raise ValueError(
        'Missing database connection type. Please define INSTANCE_CONNECTION_NAME'
    )

# This global variable is declared with a value of `None`
db = None

# Initiates connection to database
def init_db():
    global db
    db = init_connection_pool()

def create_table(db: sqlalchemy.engine.base.Engine) -> None:
    with db.connect() as conn:

        # Create the users table
        conn.execute(
            sqlalchemy.text(
               '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT AUTO_INCREMENT NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(15),
                    name VARCHAR(100),
                    role ENUM('user', 'admin') NOT NULL,
                    PRIMARY KEY (user_id)
                );
                '''
            )
        )

        conn.execute(
            sqlalchemy.text(
                '''
                CREATE TABLE IF NOT EXISTS shelters (
                    shelter_id BIGINT AUTO_INCREMENT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    zip_code VARCHAR(10),
                    user_id BIGINT NOT NULL,
                    PRIMARY KEY (shelter_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                '''
            )
        )

        conn.execute(
            sqlalchemy.text(
                '''
                CREATE TABLE IF NOT EXISTS pets (
                    pet_id BIGINT AUTO_INCREMENT NOT NULL,
                    name VARCHAR(100),
                    type ENUM('dog', 'cat', 'other'),
                    gender ENUM('male', 'female', 'unknown'),
                    news_item VARCHAR(255),
                    date_created DATETIME NOT NULL,
                    age INT,
                    breed VARCHAR(100),
                    disposition VARCHAR(255),
                    description VARCHAR(255),
                    availability ENUM('available', 'not available', 'adopted', 'pending') NOT NULL,
                    picture_url VARCHAR(255),
                    shelter_id BIGINT,
                    PRIMARY KEY (pet_id),
                    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id) ON DELETE SET NULL
                );
                '''
            )
        )

        conn.execute(
            sqlalchemy.text(
                '''
                CREATE TABLE IF NOT EXISTS favorites (
                    id BIGINT AUTO_INCREMENT NOT NULL,
                    favorited_at DATETIME NOT NULL,
                    pet_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    PRIMARY KEY (id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
                );
                '''
            )
        )
        conn.execute(
            sqlalchemy.text(
                '''
                CREATE TABLE IF NOT EXISTS pet_dispositions (
                    disposition VARCHAR(255) NOT NULL,
                    pet_id BIGINT NOT NULL,
                    FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
                );
                '''
            )
        )

        conn.commit()


@app.route('/')
def index():
    return 'Please navigate to /pets to use this API'


if __name__ == '__main__':
    init_db()
    create_table(db)
    app.run(host='0.0.0.0', port=8080, debug=True)
