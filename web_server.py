#!/usr/bin/env python3
"""
Servidor Web para Cliente MUD
Serve HTML e WebSocket gateway para conectar ao servidor MUD
"""

import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import websockets
from websockets.server import serve
from websockets.exceptions import ConnectionClosed

# Carrega variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv não instalado, usa variáveis de ambiente do sistema

# Configurações
WEB_PORT = int(os.environ.get('WEB_PORT', 80))
MUD_HOST = os.environ.get('MUD_HOST', 'localhost')
MUD_PORT = int(os.environ.get('MUD_PORT', 4000))
WS_PORT = int(os.environ.get('WS_PORT', 8080))

# Para produção, pode precisar de permissões de root para porta 80
# Alternativa: usar porta 8000 e fazer proxy reverso
if WEB_PORT == 80 and os.geteuid() != 0:
    print(f"[Aviso] Porta 80 requer privilégios de root. Usando porta 8000...")
    WEB_PORT = 8000


class WebHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servir arquivos estáticos"""
    
    def do_GET(self):
        """Serve arquivos HTML/CSS/JS"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Rota raiz serve index.html
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Lê e serve o HTML
            try:
                with open('web/index.html', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b'<h1>Arquivo index.html nao encontrado</h1>')
        else:
            # Tenta servir outros arquivos estáticos
            file_path = f'web{path}'
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                # Detecta tipo MIME
                if file_path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif file_path.endswith('.png'):
                    self.send_header('Content-type', 'image/png')
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    self.send_header('Content-type', 'image/jpeg')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 Not Found')
    
    def log_message(self, format, *args):
        """Suprime logs do servidor HTTP"""
        pass


def run_http_server():
    """Roda servidor HTTP em thread separada"""
    server = HTTPServer(('0.0.0.0', WEB_PORT), WebHandler)
    print(f"[Web Server] Servidor HTTP rodando na porta {WEB_PORT}")
    server.serve_forever()


async def mud_proxy(websocket, path):
    """
    Gateway WebSocket que faz proxy entre cliente web e servidor MUD TCP
    """
    print(f"[WebSocket] Nova conexão: {websocket.remote_address}")
    reader = None
    writer = None
    
    try:
        # Conecta ao servidor MUD TCP
        reader, writer = await asyncio.open_connection(MUD_HOST, MUD_PORT)
        print(f"[WebSocket] Conectado ao MUD em {MUD_HOST}:{MUD_PORT}")
        
        # Task para receber mensagens do MUD e enviar para o cliente
        async def mud_to_client():
            try:
                buffer = b''
                accumulated_lines = []
                flush_task = None
                
                async def delayed_flush():
                    """Envia mensagens acumuladas após um pequeno delay"""
                    current_task = asyncio.current_task()
                    await asyncio.sleep(0.05)  # Espera 50ms para acumular mais linhas
                    nonlocal accumulated_lines, flush_task
                    # Verifica se ainda é a task atual e se ainda há linhas acumuladas
                    if accumulated_lines and flush_task is current_task:
                        full_message = ''.join(accumulated_lines)
                        accumulated_lines = []
                        await websocket.send(json.dumps({'type': 'mud_output', 'data': full_message}))
                        flush_task = None
                
                async def flush_now():
                    """Envia mensagens acumuladas imediatamente"""
                    nonlocal accumulated_lines, flush_task
                    # Cancela task de flush delayado se existir
                    if flush_task and not flush_task.done():
                        flush_task.cancel()
                        try:
                            await flush_task
                        except asyncio.CancelledError:
                            pass
                        flush_task = None
                    
                    if accumulated_lines:
                        full_message = ''.join(accumulated_lines)
                        accumulated_lines = []
                        await websocket.send(json.dumps({'type': 'mud_output', 'data': full_message}))
                
                while True:
                    data = await reader.read(4096)
                    if not data:
                        # Envia qualquer coisa que sobrou
                        await flush_now()
                        break
                    
                    buffer += data
                    
                    # Processa buffer em linhas completas
                    while b'\n' in buffer:
                        idx = buffer.index(b'\n')
                        # Pega tudo até o \n incluindo \r\n ou só \n
                        if idx > 0 and buffer[idx-1:idx] == b'\r':
                            chunk = buffer[:idx+1]
                            buffer = buffer[idx+1:]
                        else:
                            chunk = buffer[:idx+1]
                            buffer = buffer[idx+1:]
                        
                        # Converte para string preservando quebras de linha
                        line = chunk.decode('utf-8', errors='replace')
                        accumulated_lines.append(line)
                        
                        # Se acumulou muitas linhas, envia imediatamente
                        if len(accumulated_lines) >= 15:
                            await flush_now()
                        else:
                            # Cancela flush anterior e agenda novo
                            if flush_task and not flush_task.done():
                                flush_task.cancel()
                            flush_task = asyncio.create_task(delayed_flush())
                    
                    # Se buffer ficou muito grande sem \n, envia de qualquer forma
                    if len(buffer) > 8192:
                        message = buffer.decode('utf-8', errors='replace')
                        buffer = b''
                        accumulated_lines.append(message)
                        await flush_now()
            except ConnectionClosed:
                pass
            except Exception as e:
                print(f"[WebSocket] Erro ao ler do MUD: {e}")
                try:
                    await websocket.send(json.dumps({'type': 'error', 'data': f'Erro na conexão: {e}'}))
                except:
                    pass
        
        # Task para receber mensagens do cliente e enviar para o MUD
        async def client_to_mud():
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get('type') == 'mud_input':
                            # Envia comando para o servidor MUD
                            command = data.get('data', '') + '\r\n'
                            writer.write(command.encode('utf-8'))
                            await writer.drain()
                    except json.JSONDecodeError:
                        # Se não for JSON, trata como comando direto (fallback)
                        command = message + '\r\n'
                        writer.write(command.encode('utf-8'))
                        await writer.drain()
            except ConnectionClosed:
                pass
            except Exception as e:
                print(f"[WebSocket] Erro ao escrever no MUD: {e}")
                try:
                    await websocket.send(json.dumps({'type': 'error', 'data': f'Erro ao enviar comando: {e}'}))
                except:
                    pass
        
        # Executa ambas as tasks em paralelo
        await asyncio.gather(mud_to_client(), client_to_mud())
        
    except Exception as e:
        print(f"[WebSocket] Erro na conexão: {e}")
        try:
            await websocket.send(json.dumps({'type': 'error', 'data': f'Erro ao conectar ao MUD: {e}'}))
        except:
            pass
    finally:
        # Fecha conexões
        if writer:
            writer.close()
            await writer.wait_closed()
        print(f"[WebSocket] Conexão fechada: {websocket.remote_address}")


async def run_websocket_server():
    """Roda servidor WebSocket"""
    print(f"[WebSocket] Servidor WebSocket rodando na porta {WS_PORT}")
    async with serve(mud_proxy, '0.0.0.0', WS_PORT):
        await asyncio.Future()  # Roda indefinidamente


async def main():
    """Função principal"""
    # Inicia servidor HTTP em thread separada
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Roda servidor WebSocket no loop principal
    await run_websocket_server()


if __name__ == '__main__':
    print("=" * 60)
    print("Servidor Web MUD")
    print("=" * 60)
    print(f"HTTP Server: http://localhost:{WEB_PORT}")
    print(f"WebSocket Server: ws://localhost:{WS_PORT}")
    print(f"MUD Server: {MUD_HOST}:{MUD_PORT}")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Servidor] Encerrando...")

