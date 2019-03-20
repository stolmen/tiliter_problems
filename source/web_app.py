"""

Tiliter candidate problem


Build the solution to 3.2 into a Django webserver with a modern front-end.
Requirements:
• Provide a file browser pop-up to selecti a vdeo file to process.
• Show information processing is in progress.
• Deliver the processed file to the default local Downloads folder

Using tornado default web server in place of Django.
"""

import os
import tornado.ioloop
import tornado.web
import tornado.gen
import video


UPLOADS_PATH = "uploads"


class ProcessVideoFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("file_upload_form.html")


class UploadVideoHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            os.mkdir(UPLOADS_PATH)
        except FileExistsError:
            pass

        file_from_request = self.request.files['file1'][0]
        file_data = file_from_request['body']
        file_name = file_from_request['filename']
        destination_file_path = os.path.join(UPLOADS_PATH, file_name)
        with open(destination_file_path, 'wb+') as output_file:
            output_file.write(file_data)
        
        base, ext = file_name.split('.')
        destination_file = base + '_processed.' + ext
        video.perform_segmentation_analysis_on_video(
            video_file_path=destination_file_path,
            destination_file=os.path.join(UPLOADS_PATH, destination_file),
        )

        self.redirect(f"/content/{destination_file}")


def make_app():
    return tornado.web.Application([
        (r"/", ProcessVideoFileHandler),
        (r"/upload", UploadVideoHandler),
        (r"/content/(.*)", tornado.web.StaticFileHandler, {"path":UPLOADS_PATH}),
    ], debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
