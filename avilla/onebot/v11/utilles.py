SPECIAL_POST_TYPE = {"message_sent": "message"}


def onebot11_event_type(raw: dict) -> str:
    return (
        f"{(post := raw['post_type'])}."
        f"{raw.get(f'{SPECIAL_POST_TYPE.get(post, post)}_type', '_')}"
        f"{f'.{sub}' if (sub:=raw.get('sub_type')) else ''}"
    )
