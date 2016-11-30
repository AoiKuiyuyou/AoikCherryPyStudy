# coding: utf-8
from __future__ import absolute_import

# Standard imports
import logging
import os.path
import sys

# External imports
import aoiktracecall.config
import aoiktracecall.logging
import aoiktracecall.state
import aoiktracecall.trace


# Traced modules should be imported after `trace_calls_in_specs` is called.


# Set configs
aoiktracecall.config.set_configs({
    # Whether use wrapper class.
    #
    # Wrapper class is more adaptive to various types of callables but will
    # break if the code that was using the original function requires a real
    # function, instead of a callable. Known cases include PyQt slot functions.
    #
    'WRAP_USING_WRAPPER_CLASS': True,

    # Whether wrap base class attributes in a subclass.
    #
    # If enabled, wrapper attributes will be added to a subclass even if the
    # wrapped original attributes are defined in a base class.
    #
    # This helps in the case that base class attributes are implemented in C
    # extensions thus can not be traced directly.
    #
    'WRAP_BASE_CLASS_ATTRIBUTES': True,

    # Indentation unit text
    'INDENT_UNIT_TEXT': ' ' * 8,

    # Whether highlight title shows `self` argument's class instead of called
    # function's defining class.
    #
    # This helps reveal the real type of the `self` argument on which the
    # function is called.
    #
    'HIGHLIGHT_TITLE_SHOW_SELF_CLASS': True,

    # Highlight title line character count max
    'HIGHLIGHT_TITLE_LINE_CHAR_COUNT_MAX': 265,

    # Whether show main thread ID
    'SHOW_MAIN_THREAD_ID': True,

    # Whether show function's file path and line number in pre-call hook
    'SHOW_FUNC_FILE_PATH_LINENO_PRE_CALL': True,

    # Whether show function's file path and line number in post-call hook
    'SHOW_FUNC_FILE_PATH_LINENO_POST_CALL': False,

    # Whether wrapper function should debug info dict's URIs
    'WRAPPER_FUNC_DEBUG_INFO_DICT_URIS': False,

    # Whether printing handler should debug arguments inspect info
    'PRINTING_HANDLER_DEBUG_ARGS_INSPECT_INFO': False,

    # Whether printing handler should debug info dict.
    #
    # Notice info dict contains called function's arguments and printing these
    # arguments may cause errors.
    #
    'PRINTING_HANDLER_DEBUG_INFO_DICT': False,

    # Whether printing handler should debug info dict, excluding arguments.
    #
    # Use this if `PRINTING_HANDLER_DEBUG_INFO_DICT` causes errors.
    #
    'PRINTING_HANDLER_DEBUG_INFO_DICT_SAFE': False,
})


# Add debug logger handler
aoiktracecall.logging.get_debug_logger().addHandler(logging.NullHandler())

# Add info logger handler
aoiktracecall.logging.get_info_logger().addHandler(
    logging.StreamHandler(sys.stdout)
)


class PerThreadLogHandler(logging.Handler):
    """
    This log handler writes log messages to a separate file for each thread.
    """

    def __init__(self, log_file_path_format, *args, **kwargs):
        # Call super constructor
        super(PerThreadLogHandler, self).__init__(*args, **kwargs)

        # Log file path format
        self._log_file_path_format = log_file_path_format

        # Dict that maps thread ID to log file
        self._map_thread_id_to_log_file = {}

    def emit(self, record):
        # Get current thread ID
        thread_id = aoiktracecall.state.get_simple_thread_id()

        # Find log file for current thread
        log_file = self._map_thread_id_to_log_file.get(thread_id, None)

        # If log file is not found
        if log_file is None:
            # Get log file path
            log_file_path = self._log_file_path_format.format(thread_id)

            # Create log file
            log_file = self._map_thread_id_to_log_file[thread_id] = open(
                log_file_path, mode='wb'
            )

        # Get log message
        message = record.message

        # If log message is not bytes
        if not isinstance(message, bytes):
            # Encode log message to bytes
            message = message.encode('utf-8')

        # Write log message
        log_file.write(message)

        # Write a newline
        log_file.write(b'\n')

        # Flush write buffer
        log_file.flush()


# Add info logger handler
aoiktracecall.logging.get_info_logger().addHandler(
    PerThreadLogHandler(
        log_file_path_format=(
            (
                # Put log file in this directory
                'D:/Demo/AoikCherryPyStudy/src/'
                # If the directory exists
                if os.path.isdir('D:/Demo/AoikCherryPyStudy/src/')
                # Else put log file in the working directory
                else './'
            ) + (
                # Log file name
                'RequestHandlerCPWSGIServerTraceCallLogPy%sThread{}.txt' %
                sys.version_info[0]
            )
        )
    )
)

# Add error logger handler
aoiktracecall.logging.get_error_logger().addHandler(
    logging.StreamHandler(sys.stderr)
)


# Constant for `highlight`
HL = 'highlight'

# Create trace specs.
#
# The order of the specs determines the matching precedence, with one exception
# that URI patterns consisting of only alphanumerics, underscores, and dots are
# considered as exact URI matching, and will have higher precedence over all
# regular expression matchings. The rationale is that a spec with exact URI
# matching is more specific therefore should not be shadowed by any spec with
# regular expression matching that has appeared early.
#
trace_specs = [
    # ----- aoiktracecall -----
    ('aoiktracecall([.].+)?', False),

    # ----- * -----
    # Tracing `__setattr__` will reveal instances' attribute assignments.
    # Notice Python 2 old-style classes have no `__setattr__` attribute.
    ('.+[.]__setattr__', False),

    # Not trace most of double-underscore functions.
    # Tracing double-underscore functions is likely to break code, e.g. tracing
    # `__str__` or `__repr__` may cause infinite recursion.
    ('.+[.]__(?!init|call)[^.]+__', False),

    # ----- socket._socketobject (Python 2), socket.socket (Python 3) -----
    # Notice in Python 2, class `socket._socketobject`'s instance methods
    # - recv
    # - recvfrom
    # - recv_into
    # - recvfrom_into
    # - send
    # - sendto
    # are dynamically generated in `_socketobject.__init__`. The approach of
    # wrapping class attributes is unable to trace these methods.

    ('socket[.](_socketobject|socket)[.]__init__', HL),

    ('socket[.](_socketobject|socket)[.]bind', HL),

    ('socket[.](_socketobject|socket)[.]listen', HL),

    ('socket[.](_socketobject|socket)[.]connect', HL),

    ('socket[.](_socketobject|socket)[.]accept', HL),

    ('socket[.](_socketobject|socket)[.]setblocking', HL),

    ('socket[.](_socketobject|socket)[.]setsockopt', HL),

    ('socket[.](_socketobject|socket)[.]settimeout', HL),

    ('socket[.](_socketobject|socket)[.]makefile', HL),

    ('socket[.](_socketobject|socket)[.]recv.*', HL),

    ('socket[.](_socketobject|socket)[.]send.*', HL),

    ('socket[.](_socketobject|socket)[.]shutdown', HL),

    ('socket[.](_socketobject|socket)[.]close', HL),

    # ----- socket._fileobject (Python 2), socket.SocketIO (Python 3) -----
    ('socket[.](SocketIO|_fileobject)[.]__init__', HL),

    ('socket[.](SocketIO|_fileobject)[.]readable', True),

    ('socket[.](SocketIO|_fileobject)[.]read.*', HL),

    ('socket[.](SocketIO|_fileobject)[.]writable', True),

    ('socket[.](SocketIO|_fileobject)[.]write.*', HL),

    ('socket[.](SocketIO|_fileobject)[.]flush', HL),

    ('socket[.](SocketIO|_fileobject)[.]close', HL),

    ('socket[.](SocketIO|_fileobject)[.].+', True),

    # ----- socket -----
    ('socket._intenum_converter', False),

    ('socket[.].+[.]_decref_socketios', False),

    ('socket[.].+[.]fileno', False),

    # Ignore to avoid error in `__repr__` in Python 3
    ('socket[.].+[.]getpeername', False),

    # Ignore to avoid error in `__repr__` in Python 3
    ('socket[.].+[.]getsockname', False),

    ('socket[.].+[.]gettimeout', False),

    ('socket([.].+)?', True),

    # ----- select (Python 2) -----
    ('select.select', HL),

    ('select([.].+)?', True),

    # ----- selectors (Python 3) -----
    ('selectors.SelectSelector.__init__', HL),

    ('selectors.SelectSelector.register', HL),

    ('selectors.SelectSelector.select', HL),

    ('selectors([.].+)?', True),

    # ----- SocketServer (Python 2), socketserver (Python 3) -----
    ('SocketServer._eintr_retry', False),

    ('(socketserver|SocketServer)[.]BaseServer[.]__init__', HL),

    ('(socketserver|SocketServer)[.]TCPServer[.]__init__', HL),

    ('(socketserver|SocketServer)[.]ThreadingMixIn[.]process_request', HL),

    (
        '(socketserver|SocketServer)[.]ThreadingMixIn[.]'
        'process_request_thread', HL
    ),

    # Ignore to avoid error:
    # ```
    # 'WSGIServer' object has no attribute '_BaseServer__is_shut_down'
    # ```
    ('(socketserver|SocketServer)[.]ThreadingMixIn[.].+', False),

    ('(socketserver|SocketServer)[.]BaseRequestHandler[.]__init__', HL),

    ('(socketserver|SocketServer)[.].+[.]service_actions', False),

    ('.+[.]server_bind', HL),

    ('.+[.]server_activate', HL),

    ('.+[.]serve_forever', HL),

    ('.+[.]_handle_request_noblock', HL),

    ('.+[.]get_request', HL),

    ('.+[.]verify_request', HL),

    ('.+[.]process_request', HL),

    ('.+[.]process_request_thread', HL),

    ('.+[.]finish_request', HL),

    ('.+[.]setup', HL),

    ('.+[.]handle', HL),

    ('.+[.]finish', HL),

    ('.+[.]shutdown_request', HL),

    ('.+[.]close_request', HL),

    ('.+[.]fileno', False),

    ('(socketserver|SocketServer)([.].+)?', True),

    # ----- mimetools -----
    # `mimetools` is used for parsing HTTP headers in Python 2.

    ('mimetools([.].+)?', False),

    # ----- email -----
    # `email` is used for parsing HTTP headers in Python 3.

    ('email([.].+)?', False),

    # ----- BaseHTTPServer (Python 2), http.server (Python 3) -----
    ('.+[.]handle_one_request', HL),

    ('.+[.]parse_request', HL, 'hide_below'),

    ('.+[.]send_response', HL),

    ('.+[.]send_header', HL),

    ('.+[.]end_headers', HL),

    # ----- BaseHTTPServer (Python 2) -----
    ('BaseHTTPServer([.].+)?', True),

    # ----- http (Python 3) -----
    # Ignore to avoid error
    ('http.cookies[.].+[.]items', False),

    ('http([.].+)?', True),

    # ----- wsgiref -----
    ('wsgiref.handlers.BaseHandler.write', HL),

    ('wsgiref.handlers.BaseHandler.close', HL),

    ('wsgiref.handlers.SimpleHandler.__init__', HL),

    ('wsgiref.handlers.SimpleHandler._write', HL),

    ('wsgiref.handlers.SimpleHandler._flush', HL),

    ('wsgiref.simple_server.WSGIServer.__init__', HL),

    ('wsgiref.simple_server.ServerHandler.__init__', HL),

    ('wsgiref.simple_server.ServerHandler.close', HL),

    ('.+[.]make_server', HL),

    ('.+[.]setup_environ', HL, 'hide_below'),

    ('.+[.]set_app', HL),

    ('.+[.]get_environ', HL, 'hide_below'),

    ('.+[.]get_app', HL),

    ('.+[.]run', HL),

    ('.+[.]start_response', HL),

    ('.+[.]finish_response', HL),

    ('.+[.]send_headers', HL),

    ('.+[.]cleanup_headers', HL),

    ('.+[.]send_preamble', HL),

    ('.+[.]finish_content', HL),

    ('.+[.]finish', HL),

    ('wsgiref([.].+)?', True),

    # ----- threading -----
    ('threading', True),

    ('threading.Thread', True),

    ('threading.Thread.__init__', HL),

    ('threading.Thread.run', HL),

    ('threading.Thread.start', HL),

    # Ignore to avoid error
    ('threading[.]Thread[.](_.+)?', False),

    # ----- cherrypy -----
    ('cherrypy._HandleSignalsPlugin.subscribe', HL),

    ('cherrypy._Serving.__init__', HL),

    ('cherrypy._Serving.clear', HL),

    ('cherrypy._Serving.load', HL),

    # This will not get expected effects because the original function has been
    # used during module loading in `cherrypy/__init__.py`:
    # ```
    # engine.timeout_monitor = _TimeoutMonitor(engine)
    # ```
    #
    ('cherrypy._TimeoutMonitor.run', HL),

    ('cherrypy._cpconfig.Config.update', HL),

    ('cherrypy._cpdispatch.Dispatcher.__init__', HL),

    ('cherrypy._cpdispatch.Dispatcher.find_handler', HL),

    ('cherrypy._cpdispatch.MethodDispatcher.__call__', HL),

    ('cherrypy._cpdispatch.PageHandler.__call__', HL),

    ('cherrypy._cpdispatch.PageHandler.__init__', HL),

    ('cherrypy._cpreqbody.Entity.__init__', HL),

    # Ignore to avoid error
    ('cherrypy._cprequest.HookMap', False),

    ('cherrypy._cpreqbody.RequestBody.__init__', HL),

    ('cherrypy._cprequest.Request.__init__', HL),

    ('cherrypy._cprequest.Request.close', HL),

    ('cherrypy._cprequest.Request.get_resource', HL),

    ('cherrypy._cprequest.Request.process_headers', HL),

    ('cherrypy._cprequest.Request.process_query_string', HL),

    ('cherrypy._cprequest.Request.respond', HL),

    ('cherrypy._cprequest.Request.run', HL),

    ('cherrypy._cprequest.Response.__init__', HL),

    ('cherrypy._cprequest.Response.finalize', HL),

    ('cherrypy._cpserver.Server.httpserver_from_self', HL),

    ('cherrypy._cpserver.Server.start', HL),

    ('cherrypy._cptools.HandlerTool.handler', HL),

    ('cherrypy._cptree.Application.__call__', HL),

    ('cherrypy._cptree.Application.__init__', HL),

    ('cherrypy._cptree.Application.find_config', HL),

    ('cherrypy._cptree.Application.get_serving', HL),

    ('cherrypy._cptree.Application.merge', HL),

    ('cherrypy._cptree.Application.release_serving', HL),

    ('cherrypy._cptree.Application.request_class', HL),

    ('cherrypy._cptree.Application.response_class', HL),

    ('cherrypy._cptree.Tree.__call__', HL),

    ('cherrypy._cptree.Tree.mount', HL),

    ('cherrypy._cpwsgi.AppResponse.__init__', HL),

    ('cherrypy._cpwsgi.AppResponse.close', HL),

    ('cherrypy._cpwsgi.AppResponse.run', HL),

    ('cherrypy._cpwsgi.AppResponse.translate_headers', HL),

    ('cherrypy._cpwsgi.CPWSGIApp.__call__', HL),

    ('cherrypy._cpwsgi.CPWSGIApp.response_class', HL),

    ('cherrypy._cpwsgi.CPWSGIApp.tail', HL),

    ('cherrypy._cpwsgi.ExceptionTrapper.__call__', HL),

    ('cherrypy._cpwsgi.InternalRedirector.__call__', HL),

    ('cherrypy._cpwsgi._TrappedResponse.__init__', HL),

    ('cherrypy._cpwsgi._TrappedResponse.close', HL),

    ('cherrypy._cpwsgi._TrappedResponse.trap', HL),

    ('cherrypy._cpwsgi_server.CPWSGIServer.__init__', HL),

    ('cherrypy.lib.encoding.ResponseEncoder.__call__', HL),

    ('cherrypy.lib.reprconf.NamespaceSet.__call__', HL),

    ('cherrypy.process.plugins.BackgroundTask.__init__', HL),

    ('cherrypy.process.plugins.Monitor.start', HL),

    ('cherrypy.process.plugins.ThreadManager.acquire_thread', HL),

    ('cherrypy.process.servers.ServerAdapter._start_http_thread', HL),

    ('cherrypy.process.servers.ServerAdapter.start', HL),

    ('cherrypy.process.servers.ServerAdapter.wait', HL),

    ('cherrypy.process.servers.wait_for_free_port', HL),

    ('cherrypy.process.servers.wait_for_occupied_port', HL),

    ('cherrypy.process.win32.ConsoleCtrlHandler.start', HL),

    ('cherrypy.process.win32.Win32Bus.wait', HL),

    ('cherrypy.process.wspbus.Bus.block', HL),

    ('cherrypy.process.wspbus.Bus.log', 'hide_below'),

    ('cherrypy.process.wspbus.Bus.publish', HL),

    ('cherrypy.process.wspbus.Bus.publish', HL),

    ('cherrypy.process.wspbus.Bus.start', HL),

    ('cherrypy.quickstart', HL),

    ('cherrypy.wsgiserver.CherryPyWSGIServer.ConnectionClass', HL),

    ('cherrypy.wsgiserver.CherryPyWSGIServer.__init__', HL),

    ('cherrypy.wsgiserver.HTTPConnection.RequestHandlerClass', HL),

    ('cherrypy.wsgiserver.HTTPConnection.__init__', HL),

    ('cherrypy.wsgiserver.HTTPConnection.close', HL),

    ('cherrypy.wsgiserver.HTTPConnection.communicate', HL),

    ('cherrypy.wsgiserver.HTTPRequest.__init__', HL),

    ('cherrypy.wsgiserver.HTTPRequest.parse_request', HL),

    ('cherrypy.wsgiserver.HTTPRequest.respond', HL),

    ('cherrypy.wsgiserver.HTTPRequest.send_headers', HL),

    ('cherrypy.wsgiserver.HTTPRequest.write', HL),

    ('cherrypy.wsgiserver.HTTPServer.ConnectionClass', HL),

    ('cherrypy.wsgiserver.HTTPServer.bind', HL),

    ('cherrypy.wsgiserver.HTTPServer.start', HL),

    ('cherrypy.wsgiserver.HTTPServer.tick', HL),

    ('cherrypy.wsgiserver.KnownLengthRFile.__init__', HL),

    ('cherrypy.wsgiserver.KnownLengthRFile.read', HL),

    ('cherrypy.wsgiserver.ThreadPool.__init__', HL),

    ('cherrypy.wsgiserver.ThreadPool.start', HL),

    ('cherrypy.wsgiserver.WSGIGateway.__init__', HL),

    ('cherrypy.wsgiserver.WSGIGateway.respond', HL),

    ('cherrypy.wsgiserver.WSGIGateway.start_response', HL),

    ('cherrypy.wsgiserver.WSGIGateway.write', HL),

    ('cherrypy.wsgiserver.WorkerThread.__init__', HL),

    ('cherrypy.wsgiserver.prevent_socket_inheritance', HL),

    ('cherrypy([.].+)?', True),

    # ----- __main__ -----
    ('__main__.main', HL),

    ('__main__.CustomRequestHandler', True),

    ('__main__.CustomRequestHandler.__init__', HL),

    ('__main__.CustomRequestHandler.POST', HL),
]


# Create printing handler filter function
def printing_handler_filter_func(info):
    # Get current thread ID
    current_thread_id = aoiktracecall.state.get_simple_thread_id()

    # Enabled thread id.
    # Can be set to specific thread ID to show that thread only.
    #
    shown_thread_id = current_thread_id

    # If current thread ID is not EQ shown thread id
    if current_thread_id != shown_thread_id:
        # Return None to disable the printing
        return None

    # Get onwrap URI
    onwrap_uri = info['onwrap_uri']

    # If onwrap URI is one of these URIs
    if onwrap_uri in [
        # In Python 2
        'socket._fileobject.readinto',
        # In Python 3
        'socket.SocketIO.readinto',
        # In Python 2
        'socket._socketobject.recv_into',
        # In Python 3
        'socket.socket.recv_into',
    ]:
        # Get arguments inspect info
        arguments_inspect_info = info['arguments_inspect_info']

        # If have arguments inspect info.
        # This is the case for `readinto`.
        if arguments_inspect_info is not None:
            # Get `b` argument info
            arg_info = arguments_inspect_info.fixed_arg_infos.get('b', None)

            # If have argument info
            if arg_info is not None:
                # Replace the argument with an empty `bytearray` to hide the
                # random bytes in the original argument
                arg_info.value = bytearray()

        # If not have arguments inspect info.
        # This is the case for `recv_into`.
        else:
            # Get positional arguments
            args = info['args']

            # If positional argument count is GE 2
            if len(args) >= 2:
                # If the second argument is `bytearray` instance
                if isinstance(args[1], bytearray):
                    # Get arguments to be printed
                    args_printed = list(args)

                    # Replace the second argument with an empty `bytearray` to
                    # hide the random bytes in the original argument
                    args_printed[1] = bytearray()

                    # Set arguments to be printed
                    info['args_printed'] = args_printed

    # Return info dict
    return info


# Trace calls according to trace specs.
#
# This function will hook the module importing system in order to intercept and
# process newly imported modules. Callables in these modules which are matched
# by one of the trace specs will be wrapped to enable tracing.
#
# Already imported modules will be processed as well. But their callables may
# have been referenced elsewhere already, making the tracing incomplete. This
# explains why import hook is needed and why modules must be imported after
# `trace_calls_in_specs` is called.
#
aoiktracecall.trace.trace_calls_in_specs(
    specs=trace_specs,
    printing_handler_filter_func=printing_handler_filter_func,
)


# Import modules after `trace_calls_in_specs` is called
import cherrypy


class CustomRequestHandler(object):
    """
    This request handler echoes request body in response body.
    """

    # Set `exposed` be True
    exposed = True

    def POST(self, *args, **kwargs):
        # Get environ dict
        environ = cherrypy.request.wsgi_environ

        # Get `Context-Length` header value
        content_length_text = environ['CONTENT_LENGTH']

        # If header value is empty
        if not content_length_text:
            # Set content length be 0
            content_length = 0

        # If header value is not empty
        else:
            # Convert to int
            content_length = int(content_length_text)

        # Read request body
        #
        # Notice calling `cherrypy.request.body.read` will raise error, so read
        # from `fp` directly.
        #
        request_body = cherrypy.request.body.fp.read(content_length)

        # Return response body
        return request_body


def main():
    try:
        # Create config
        config = {
            'global': {
                'server.socket_host': '127.0.0.1',
                'server.socket_port': 8000,
                'server.thread_pool': 1,
                'engine.autoreload.on': False,
            },
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'request.process_request_body': False,
                'tools.response_headers.on': True,
                'tools.response_headers.headers':
                    [('Content-Type', 'text/plain')],
            }
        }

        # Run server
        cherrypy.quickstart(
            CustomRequestHandler(),
            config=config,
        )

    # If have `KeyboardInterrupt`
    except KeyboardInterrupt:
        # Stop gracefully
        pass


# Trace calls in this module.
#
# Calling this function is needed because at the point `trace_calls_in_specs`
# is called, this module is being initialized, therefore callables defined
# after the call point are not accessible to `trace_calls_in_specs`.
#
aoiktracecall.trace.trace_calls_in_this_module()


# If is run as main module
if __name__ == '__main__':
    # Call main function
    exit(main())
