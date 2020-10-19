import re
import traceback

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    body = ['<body style="text-align: center;margin: 0 25%; border-left: .1rem dotted gray; border-right: .1rem dotted gray;">']
    page = """
        <h1>{title}</h1>
        <table>
            <tr><th>Author</th><td>{author}</td></tr>
            <tr><th>Publisher</th><td>{publisher}</td></tr>
            <tr><th>ISBN</th><td>{isbn}</td></tr>
        </table>
        <a href="/">Back to the list</a>
        """
    book = DB.title_info(book_id)
    if book is None:
        raise NameError

    body.append('<hr>')
    body.append(page.format(**book))
    body.append('<hr>')
    body.append('</body>')
    return '\n'.join(body)


def books():
    all_books = DB.titles()

    body = ['<h1>My Library</h1>']
    body.append('<table>')
    count = 1
    row = '<tr><td>{}) </td><td><a href="/book/{id}">{title}</a></td></tr>'

    for book in all_books:
        body.append(row.format(count, **book))
        count += 1
    body.append('</table>')
    return '\n'.join(body)

def resolve_path(path):
    funcs = {
        'default': books,
        'book': book,
    }

    path = path.strip('/').split('/')

    func_name = 'default' if path[0] == '' else path[0]
    args = path[1:]

    try:
        func = funcs[func_name]
    except KeyError:
        raise NameError

    return func, args

def application(environ, start_response):
    headers = [("Content-type", "text/html")]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        func, args = resolve_path(path)
        body = func(*args)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>Internal Server Error</h1>"
        print(traceback.format_exc())
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
