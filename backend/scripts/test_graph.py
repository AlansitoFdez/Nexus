"""Script suelto para probar el grafo completo end-to-end (no un test formal)."""

import asyncio
from app.agents.graph import build_graph


async def main():
    graph = await build_graph()

    initial_state = {
        "ticket_id": 5,  # sustituye por el id real de un ticket que ya exista
        "original_text": "llevo dos meses pagando el doble en mi suscripción por un error de facturación, necesito que me devolváis el dinero cobrado de más",
        "cleaned_text": None,
        "classification": None,
        "urgency": None,
        "confidence": None,
        "kb_documents": [],
        "similar_tickets": [],
        "diagnosis": None,
        "diagnosis_confidence": None,
        "proposed_response": None,
        "pending_actions": [],
        "escalated": False,
        "node_history": [],
        "error": None,
    }

    config = {"configurable": {"thread_id": "5"}}
    result = await graph.ainvoke(initial_state, config=config)
    print(result)


asyncio.run(main())