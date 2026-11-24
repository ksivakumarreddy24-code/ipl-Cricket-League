
from fastapi import FastAPI, HTTPException,Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import functions

app = FastAPI()