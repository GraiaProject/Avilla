import json
import re


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unescape(s: str) -> str:
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def handle_text(msg: str):
    text_begin = 0
    msg = msg.replace("@everyone", "")
    for embed in re.finditer(
        r"\<(?P<type>(?:@|#|emoji:))!?(?P<id>\w+?)\>",
        msg,
    ):
        if content := msg[text_begin : embed.pos + embed.start()]:
            yield {"type": "text", "text": unescape(content)}
        text_begin = embed.pos + embed.end()
        if embed["type"] == "@":
            yield {"type": "mention", "user_id": embed.group("id")}
        elif embed["type"] == "#":
            yield {"type": "mention", "channel_id": embed.group("id")}
        else:
            yield {"type": "emoji", "id": embed.group("id")}
    if content := msg[text_begin:]:
        yield {"type": "text", "text": unescape(content)}


def pre_deserialize(message: dict) -> list[dict]:
    res = []
    if message_reference := message.get("message_reference"):
        res.append({"type": "message_reference", **message_reference})
    if message.get("mention_everyone", False):
        res.append({"type": "mention_everyone"})
    if "content" in message:
        res.extend(handle_text(message["content"]))
    if attachments := message.get("attachments"):
        res.extend({"type": "attachment", "url": i["url"]} for i in attachments if i["url"])
    if embeds := message.get("embeds"):
        res.extend({"type": "embed", **i} for i in embeds)
    if ark := message.get("ark"):
        res.append({"type": "ark", **ark})
    return res


def pro_serialize(message: list[dict]):
    res = {}
    content = ""
    for elem in message:
        if elem["type"] == "mention_everyone":
            content += "@everyone"
        elif elem["type"] == "mention_user":
            content += f"<@{elem['user_id']}>"
        elif elem["type"] == "mention_channel":
            content += f"<#{elem['channel_id']}"
        elif elem["type"] == "emoji":
            content += f"<emoji:{elem['id']}>"
        elif elem["type"] == "text":
            content += escape(elem["text"])
        elif elem["type"] == "attachment":
            res["image"] = elem["url"]
        elif elem["type"] == "local_iamge":
            res["file_image"] = elem["content"]
        elif elem["type"] == "embed":
            res["embed"] = elem
            res["embed"].pop("type")
        elif elem["type"] == "ark":
            res["ark"] = elem
            res["ark"].pop("type")
        elif elem["type"] == "message_reference":
            res["message_reference"] = elem
            res["message_reference"].pop("type")
    if content:
        res["content"] = content
    return res


def form_data(message: dict):
    if not (file_image := message.pop("file_image", None)):
        return "post", message
    files = {"file_image": {"value": file_image, "content_type": None, "filename": "file_image"}}
    data_ = {}
    for key, value in message.items():
        if isinstance(value, (list, dict)):
            files[key] = {
                "value": json.dumps({key: value}).encode("utf-8"),
                "content_type": "application/json",
                "filename": f"{key}.json"
            }
        else:
            data_[key] = value
    return "multipart", {"files": files, "data": data_}
