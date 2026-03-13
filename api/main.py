from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import app as agent_app

app = FastAPI()

# UI'dan gelen yeni yapıya uygun model
class AnalyzeRequest(BaseModel):
    case: str
    top_k: int

@app.post("/run")
async def run_task(request: AnalyzeRequest):
    try:
        # AgentState yapısına uygun başlangıç verisi
        initial_state = {
            "case": request.case,
            "top_k": request.top_k,
            "specialist_outputs": []
        }
        
        result = agent_app.invoke(initial_state)
        
        return {
            "final_summary": result.get("final_summary", "Özet oluşturulamadı."),
            "selected": result.get("selected_specialists", [])
        }
    except Exception as e:
        print(f"HATA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))