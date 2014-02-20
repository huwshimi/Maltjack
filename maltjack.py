import argparse
import os
import shutil
import SimpleHTTPServer
import SocketServer

from jinja2 import Environment, FileSystemLoader


PORT = 8000
BUILD_DIR = 'build'
CONTENT_DIR = 'content'

def build_site(root_dir):
    env = Environment(loader=FileSystemLoader(root_dir))
    content_dir = os.path.join(root_dir, 'content')
    build_dir = os.path.join(root_dir, BUILD_DIR)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    for root, dirs, filenames in os.walk(content_dir):
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

def run_server(root_dir):
    os.chdir(os.path.join(root_dir, BUILD_DIR))
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print ("Maltjack is serving at http://localhost:%s/\n"
           "Press ctrl+c to stop." % PORT)
    httpd.serve_forever()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    build_site(args.directory)
    run_server(args.directory)
