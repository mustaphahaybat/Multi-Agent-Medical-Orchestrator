import os
import re
import operator
from typing import Annotated, List, TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

SPECIALISTS = {
    "Kardiyolog": "Kalp ve damar sagligi uzmani.",
    "Norolog": "Beyin ve sinir sistemi uzmani.",
    "Dermatolog": "Cilt hastaliklari uzmani.",
    "Onkolog": "Kanser hastaliklari uzmani.",
    "Romatolog": "Eklem ve kas agrilari uzmani.",
    "Psikiyatrist": "Ruh sagligi ve hastaliklari uzmani.",
    "Gastroenterolog": "Sindirim sistemi uzmani."
}

class AgentState(TypedDict):
    case: str
    top_k: int
    selected_specialists: List[str]
    specialist_outputs: Annotated[List[str], operator.add]
    final_summary: str

def supervisor_node(state: AgentState):
    print(f"--- YÖNETİCİ: {state['top_k']} UZMAN SEÇİYOR ---")
    specialist_desc = "\n".join([f"- {k}: {v}" for k, v in SPECIALISTS.items()])
    prompt = f"Vaka: {state['case']}\n\nUzmanlar:\n{specialist_desc}\n\nBu vaka için en ilgili {state['top_k']} uzmanın ismini aralarına virgül koyarak yaz."
    
    response = llm.invoke([HumanMessage(content=prompt)])
    selected = [s.strip() for s in response.content.split(",") if s.strip() in SPECIALISTS]
    return {"selected_specialists": selected[:state['top_k']]}

def specialist_node(state: AgentState):
    # Bu örnekte basitlik için seçilen uzmanları sırayla döneceğiz 
    # (Gerçek paralel yapı için 'Send' objesi gerekir, ancak bu aşamada bu yapı en güvenlisidir)
    outputs = []
    for expert in state["selected_specialists"]:
        print(f"--- {expert} ANALİZ EDİYOR ---")
        prompt = f"{expert} uzmanı olarak şu vakayı analiz et ve önerilerini yaz: {state['case']}"
        response = llm.invoke([HumanMessage(content=prompt)])
        outputs.append(f"[{expert}]: {response.content}")
    return {"specialist_outputs": outputs}

def aggregator_node(state: AgentState):
    print("--- AGGREGATOR: SENTEZLENİYOR ---")
    all_analyses = "\n\n".join(state["specialist_outputs"])
    prompt = f"Şu uzman analizlerini tek bir profesyonel tıbbi özete dönüştür:\n\n{all_analyses}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_summary": response.content}

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("specialists", specialist_node)
workflow.add_node("aggregator", aggregator_node)

workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "specialists")
workflow.add_edge("specialists", "aggregator")
workflow.add_edge("aggregator", END)

app = workflow.compile()