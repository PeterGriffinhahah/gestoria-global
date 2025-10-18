from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI(title="GestorIA API", description="API para análisis contable automático")

# Configurar CORS para permitir todas las origins (en producción restringir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analizar-csv")
async def analizar_csv(file: UploadFile = File(...)):
    try:
        # Leer el archivo CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Análisis básico
        ingresos = df[df['Importe'] > 0]['Importe'].sum()
        gastos = df[df['Importe'] < 0]['Importe'].sum() * -1
        beneficio = ingresos - gastos
        iva_estimado = (ingresos * 0.21) - (gastos * 0.21)
        
        return {
            "status": "success",
            "data": {
                "ingresos": round(ingresos, 2),
                "gastos": round(gastos, 2),
                "beneficio": round(beneficio, 2),
                "iva_estimado": round(iva_estimado, 2),
                "margen_beneficio": round((beneficio / ingresos * 100), 2) if ingresos > 0 else 0
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Error procesando archivo: {str(e)}"}

@app.get("/")
def root():
    return {"status": "success", "message": "GestorIA API funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
