# Deploy no Railway

## Importante: Conexões TCP no Railway

O Railway **não expõe portas TCP diretamente** por padrão. Ele foi projetado para aplicações HTTP/HTTPS. Para conectar via Telnet ou TinTin++ diretamente, você tem algumas opções:

### Opção 1: Usar Railway TCP Proxy (Recomendado)

1. No Railway, vá em **Settings** do seu serviço
2. Adicione uma **Public TCP Proxy**
3. Configure a porta interna (8080) e a porta externa que o Railway fornecerá
4. Use o domínio TCP fornecido pelo Railway para conectar

### Opção 2: Usar um VPS (Alternativa Recomendada)

Para um MUD, é recomendado usar um VPS que suporte conexões TCP diretas:
- **DigitalOcean Droplet**
- **Linode**
- **Vultr**
- **AWS EC2**
- **Google Cloud Compute Engine**

### Opção 3: Variáveis de Ambiente

Configure no Railway:
- `PORT`: A porta que o Railway atribuir (geralmente através da variável PORT)
- O servidor já está configurado para usar `os.environ.get('PORT', 4000)`

## Configuração no Railway

1. **Conecte seu repositório** ao Railway
2. **Configure o Builder**: 
   - Se usar Dockerfile: O Railway detectará automaticamente
   - Se usar Nixpacks: O Railway usará o `nixpacks.toml`
3. **Configure as variáveis de ambiente** (se necessário):
   - `PORT`: Será definido automaticamente pelo Railway
4. **Deploy**: O Railway fará o build e deploy automaticamente

## Resolução de Problemas de Build

Se o build falhar com erro de `pip: command not found`:

1. **Opção 1: Usar Dockerfile** (recomendado)
   - O arquivo `Dockerfile` já está incluído no projeto
   - O Railway detectará automaticamente

2. **Opção 2: Corrigir Nixpacks**
   - O arquivo `nixpacks.toml` já está configurado corretamente
   - Se ainda houver problemas, force o uso do Dockerfile nas configurações do Railway

## Verificando se o Servidor Está Funcionando

Após o deploy, verifique os logs:
- Você deve ver: "✓ Servidor escutando em: ..."
- Você deve ver: "✓ Servidor pronto para receber conexões!"

## Testando a Conexão

Se o Railway fornecer um proxy TCP:
```bash
telnet <railway-tcp-proxy-domain> <porta>
```

Ou usando TinTin++:
```
#session mud_local <railway-tcp-proxy-domain> <porta>
```

## Notas Importantes

- O Railway **não suporta conexões TCP diretas** sem um proxy TCP adicional
- Para produção, considere usar um VPS dedicado
- Para desenvolvimento local, use `localhost` normalmente

