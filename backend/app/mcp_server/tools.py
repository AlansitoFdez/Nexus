"""MCP tools for Nexus.

query_tickets_db se retira junto con el resto del dominio de tickets —
dependía de TicketRepository, que ya no existe. Pendiente de
reconstrucción (Fase 3.1 en adelante): read_repository_files,
get_pr_diff, post_pr_comment. Hasta entonces, el servidor MCP no
expone ninguna tool.
"""

from app.mcp_server.instance import mcp