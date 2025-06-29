from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import routes  # Asegúrate que este archivo tenga `router = APIRouter()` definido

app = FastAPI()

# Middleware CORS para permitir acceso desde la app móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cámbialo a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agrega tus rutas agrupadas (usa prefix si quieres)
app.include_router(routes.router)
