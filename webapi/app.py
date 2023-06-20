from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask, request, jsonify
import uvicorn
import asyncpg


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your specific allowed origins
    allow_methods=["*"],  # Replace with your specific allowed HTTP methods
    allow_headers=["*"],  # Replace with your specific allowed headers
)
connection_config = {
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432",
    "database": "postgres"
}

async def create_connection():
    return await asyncpg.connect(**connection_config)

async def close_connection(connection):
    await connection.close()

async def fetch_all_disasters():
    connection = await create_connection()
    result = await connection.fetch('select d.disaster_id, d.dis_date, d.dis_country, d.dis_category, d.disaster_type, d.dis_name, d.dis_source_url, d.dis_status, l.click_count from disaster_table as d full outer join link_click_count as l on d.disaster_id=l.disaster_id order by d.dis_date desc')
    await close_connection(connection)
    return result

async def update_click_count(disasterid):
    connection = await create_connection()
    
    query= "update link_click_count set click_count=click_count+1 where disaster_id=$1"
    await connection.execute(query , disasterid)
    await close_connection(connection)
    return []   
@app.post("/clickcount")
async def post_data(data: dict):
    # Extract values from the request body
    value1 = data.get('disaster_id')
    await update_click_count(value1)
    # Perform some operations with the values
    

    # Return a JSON response with the result
    response = {'successful'}
    return response
@app.get("/disaster")
async def get_disasters():
    try:
        disasters = await fetch_all_disasters()
        return disasters
    except Exception as e:
        print(f"Error retrieving disasters: {e}")
        return []


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
