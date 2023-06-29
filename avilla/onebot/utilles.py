def onebot11_event_type(raw: dict) -> str:
    return (
        f"{(post := raw['post_type'])}." f"{raw[f'{post}_type']}" f"{f'.{sub}' if (sub:=raw.get('sub_type')) else ''}"
    )
