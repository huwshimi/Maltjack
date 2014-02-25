#!/usr/bin/env python

import argparse
import scss
import os
import shutil
import SimpleHTTPServer
import SocketServer

from jinja2 import Environment, FileSystemLoader


ARGS = None
PORT = 8000
BUILD_DIR = 'build'
CONTENT_DIR = 'content'
MEDIA_DIR = 'media'
IMAGE_DIR = 'images'

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        path = path.strip('/')
        path_start = path.split('/')[0]
        if path_start != MEDIA_DIR and path_start != IMAGE_DIR:
            file_path = os.path.join(ARGS.directory, BUILD_DIR)
            filename =  os.path.join(file_path, '%s.html' % path)
            if os.path.isfile(filename):
                return filename
            else:
                return os.path.join(file_path, path, 'index.html')
        else:
            return os.path.join(ARGS.directory, BUILD_DIR, path)

    def do_GET(self):
        build_site(ARGS.directory)
        os.chdir(os.path.join(ARGS.directory, BUILD_DIR))
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

def build_site(project_dir):
    build_dir = os.path.join(project_dir, BUILD_DIR)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    build_pages(project_dir, build_dir)
    build_media(project_dir, build_dir)

def build_pages(project_dir, build_dir):
    env = Environment(loader=FileSystemLoader(project_dir))
    content_dir = os.path.join(project_dir, 'content')

    for root, dirs, filenames in os.walk(content_dir):
        if root.rsplit('/', 1)[1] != IMAGE_DIR:
            for f in filenames:
                filename = os.path.join(root, f)
                file_relative = filename.replace(content_dir + '/', '')
                build_path = os.path.join(build_dir, file_relative)
                if not os.path.exists(os.path.dirname(build_path)):
                    os.makedirs(os.path.dirname(build_path))
                template = env.get_template('%s/%s' % (CONTENT_DIR, file_relative))
                rendered = template.render()
                with open(build_path, 'w') as f:
                    f.write(rendered)

def build_scss(media_build):
    css_dir = os.path.join(media_build, 'css')
    scss.config.LOAD_PATHS = [css_dir]
    css = scss.Scss()

    for root, dirs, filenames in os.walk(css_dir):
        for f in filenames:
            if f.rsplit('.', 1)[1] == 'scss' and f[:1] != '_':
                filename = os.path.join(root, f)
                new_file = '%s.css' % filename.rsplit('.', 1)[0]
                os.chdir(root)
                with open(filename, 'r') as f:
                    compiled = css.compile(f.read())
                with open(new_file, 'w') as f:
                    f.write(compiled)

    for root, dirs, filenames in os.walk(css_dir):
        for f in filenames:
            if f.rsplit('.', 1)[1] == 'scss':
                os.remove(os.path.join(root, f))

def build_media(project_dir, build_dir):
    media_dir = os.path.join(project_dir, 'template', MEDIA_DIR)
    media_build = os.path.join(build_dir, MEDIA_DIR)
    shutil.copytree(media_dir, media_build)
    build_scss(media_build)

def run_server(project_dir):
    os.chdir(os.path.join(project_dir, BUILD_DIR))
    Handler = ServerHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print ("Maltjack is serving at http://localhost:%s/\n"
           "Press ctrl+c to stop." % PORT)
    httpd.serve_forever()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    return parser.parse_args()

if __name__ == "__main__":
    ARGS = get_args()
    build_site(ARGS.directory)
    run_server(ARGS.directory)
