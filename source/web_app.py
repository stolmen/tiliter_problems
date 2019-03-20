import tornado.ioloop
import tornado.web


"""

Tiliter candidate problem


Build the solution to 3.2 into a Django webserver with a modern front-end.
Requirements:
• Provide a file browser pop-up to selecti a vdeo file to process.
• Show information processing is in progress.
• Deliver the processed file to the default local Downloads folder

Using tornado default web server in place of Django.
"""


class ProcessVideoFileHandler(tornado.web.RequestHandler):
    def get(self):
        # TODO: write front end with a form
        # that opens a file dialogue
        self.render("file_upload_form.html")


class UploadVideoHandler(tornado.web.RequestHandler):
    def post(self):
        # TODO:
        # 1) write incoming file data to disk
        # 2) Use `video` module to process file
        # 3) Present the processed file as download
        pass


def make_app():
    return tornado.web.Application([
        (r"/", ProcessVideoFileHandler),
        (r"/upload", UploadVideoHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
