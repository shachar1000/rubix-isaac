import os
import posixpath
import hashlib

from werkzeug.exceptions import NotFound

from flask import current_app, request, Response
from flask import _app_ctx_stack as stack

import sass


class Sass(object):
    """
    `files`
        A dictionary mapping output file path (without extension) to the
        root input sass or scss file.  The input file is searched for
        relative to the application resource root.
    `app`
        A flask application to bind the extension to.
    `url_path`
        A prefix to add to the path of the url of the generated css.
    `endpoint`
        A string that can be passed to `url_for` to find the url for a
        generated css file.  Defaults to `sass`.
    `include_paths`
        A list of directories for scss to search for included files.
        Relative paths are resolved from pwd.  Using
        `pkg_resources.resource_filename` is recommended. The directory
        containing the root input file takes priority.
    `output_style`
        A string specifiying how the generated css should appear.  One of
        `"nested"`, `"expanded"` `"compact"` or `"compressed"`.  Defaults
        to `"nested"`.  See the libsass documentation for details.
    """
    _output_styles = {
        'nested': sass.SASS_STYLE_NESTED,
        'expanded': sass.SASS_STYLE_EXPANDED,
        'compact': sass.SASS_STYLE_COMPACT,
        'compressed': sass.SASS_STYLE_COMPRESSED,
    }

    def __init__(self, files, app=None,
                 url_path='/css', endpoint='sass',
                 include_paths=None, output_style=None):
        self._files = files
        self._url_path = url_path
        self._endpoint = endpoint
        self._include_paths = ','.join(include_paths).encode()
        self._output_style = self._output_styles.get(
            output_style, sass.SASS_STYLE_NESTED
        )

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.add_url_rule(
            posixpath.join(self._url_path, '<path:filename>.css'),
            endpoint=self._endpoint,
            view_func=self._send_css
        )

    def _compile(self, filename):
        input_file = os.path.join(
            current_app.root_path,
            self._files[filename]
        ).encode()

        return sass.compile_file(
            input_file,
            include_paths=self._include_paths,
            output_style=self._output_style
        )

    def _send_css(self, filename):
        if filename not in self._files:
            raise NotFound()

        rebuild = current_app.config.get('SASS_REBUILD', False)

        if not rebuild:
            if not hasattr(stack.top, 'sass_cache'):
                stack.top.sass_cache = {}
            cache = stack.top.sass_cache

            if filename not in cache:
                css = self._compile(filename)
                etag = hashlib.sha1(css).hexdigest()
                cache[filename] = (css, etag)
            else:
                css, etag = cache[filename]

            response = Response(css, content_type='text/css')
            response.set_etag(etag)
            response.make_conditional(request)

            return response

        else:
            css = self._compile(filename)
            return Response(css, content_type='text/css')
