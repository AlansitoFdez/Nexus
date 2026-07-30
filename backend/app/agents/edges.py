"""Conditional edges routing tickets between nodes in the code-review graph.

Pendiente de reconstrucción (Fase 2.4): route_after_entry,
route_after_classifier, route_after_kb_searcher, route_after_diagnosis
y route_after_human_approval se eliminaron — enrutaban entre nodos del
dominio de tickets ya eliminados en la limpieza de la Fase 1.3
(classifier_node, kb_searcher_node, diagnosis_node, response_node,
escalation_node). No tienen equivalente por adaptación: la 2.4 introduce
fan-out dinámico (edges estáticos con guardia interna, o Send()), un
problema estructuralmente distinto a "una rama, un destino" que era todo
lo que este archivo resolvía hasta ahora.
"""