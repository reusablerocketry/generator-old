#!/usr/bin/python3

import os
import http.server
import socketserver

def start_server():
  os.chdir('output')
  httpd = socketserver.TCPServer(('', 8000), http.server.SimpleHTTPRequestHandler)
  httpd.serve_forever()

def deploy_github():
  print('Rebuilding local copy...')
  os.system('./build.sh')
  # print('Build complete. Check http://localhost:8000/ for any errors. Ctrl-C when done.')
  print('Build complete.')

  if False:
    try:
      start_server()
    except KeyboardInterrupt:
      os.chdir('..')
    
  print('Deploy to GitHub Pages?')
  i = input('[yes]/no: ').strip().lower()

  if i != 'yes':
    print('Did not deploy to GitHub Pages.')
    return

  print('Deploying to GitHub Pages...')
  os.system('./deploy-github.sh')
  print('Deploy complete.')

if __name__ == '__main__':
  deploy_github()
