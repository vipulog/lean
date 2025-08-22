import secretstorage

SERVICE_NAME = "lean-app"
COLLECTION_LABEL = "Lean Application Secrets"
GEMINI_API_KEY_LABEL = "Gemini API Key"


def get_secret_collection():
    bus = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(bus)
    if collection.is_locked():
        collection.unlock()
    return collection


def store_api_key(api_key: str):
    collection = get_secret_collection()
    attributes = {"type": "api_key", "service": SERVICE_NAME}
    # Check if an item with the same attributes already exists
    for item in collection.search_items(attributes):
        if item.get_label() == GEMINI_API_KEY_LABEL:
            item.delete()
            break
    collection.create_item(GEMINI_API_KEY_LABEL, attributes, api_key, replace=True)


def retrieve_api_key() -> str | None:
    collection = get_secret_collection()
    attributes = {"type": "api_key", "service": SERVICE_NAME}
    for item in collection.search_items(attributes):
        if item.get_label() == GEMINI_API_KEY_LABEL:
            return item.get_secret().decode("utf-8")
    return None
