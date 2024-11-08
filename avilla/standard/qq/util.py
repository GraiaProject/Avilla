import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.set_ciphers("DEFAULT")
