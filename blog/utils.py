def uploaded_filename(filename, request):
    # filename generator base on time
    from datetime import datetime
    from random import choice
    from string import ascii_letters
    new_file_name=f"media_{choice(seq=ascii_letters)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{filename.split('.')[-1]}"
    return new_file_name