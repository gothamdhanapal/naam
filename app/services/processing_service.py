from app.agents.understanding_agent import understand_message
from app.repositories.inbox_repository import update_ai_result


def process_inbox_item(
    inbox_id: str,
    content: str
):

    result = understand_message(content)

    update_ai_result(
        inbox_id,
        result.model_dump()
    )

    return result