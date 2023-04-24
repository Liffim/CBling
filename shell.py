import cbling

while True:
    text = input('cbling > ')
    result, error = cbling.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)