# Guia de Contribuição

<div align="center">
  <img src="docs/openmud.png" alt="OpenMud Logo" width="400">
</div>

Obrigado por considerar contribuir com o OpenMud MUD! Este documento fornece diretrizes para contribuir com o projeto.

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug:

1. Verifique se o bug já não foi reportado nas [Issues](../../issues)
2. Se não foi reportado, crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. comportamento atual
   - Versão do Python e sistema operacional
   - Logs relevantes (se houver)

### Sugerindo Melhorias

Para sugerir novas funcionalidades:

1. Verifique se a sugestão já não existe nas [Issues](../../issues)
2. Crie uma nova issue com:
   - Descrição clara da funcionalidade
   - Casos de uso e benefícios
   - Exemplos de como seria usado

### Submetendo Pull Requests

1. **Fork o projeto** e clone seu fork
2. **Crie uma branch** para sua feature/correção:
   ```bash
   git checkout -b feature/minha-feature
   ```
3. **Faça suas alterações** seguindo os padrões do projeto
4. **Teste suas alterações** antes de submeter
5. **Commit suas mudanças** com mensagens descritivas:
   ```bash
   git commit -m "Adiciona funcionalidade X"
   ```
6. **Push para sua branch**:
   ```bash
   git push origin feature/minha-feature
   ```
7. **Abra um Pull Request** descrevendo suas mudanças

## Padrões de Código

### Python

- Use **Python 3.7+** (compatibilidade mínima)
- Siga **PEP 8** para estilo de código
- Use **docstrings** para documentar funções e classes
- Prefira **type hints** quando possível
- Mantenha linhas com no máximo 100 caracteres

### Estrutura de Arquivos

- Mantenha imports organizados (stdlib, third-party, local)
- Separe lógica de negócio de apresentação
- Use nomes descritivos para variáveis e funções

### Exemplo de Docstring

```python
def move_player(player: Player, direction: str) -> bool:
    """
    Move um jogador na direção especificada.
    
    Args:
        player: Instância do jogador a mover
        direction: Direção do movimento (norte, sul, leste, oeste)
    
    Returns:
        True se o movimento foi bem-sucedido, False caso contrário
    """
    pass
```

## Testes

Ao adicionar novas funcionalidades:

1. Teste manualmente antes de submeter
2. Certifique-se de que não quebrou funcionalidades existentes
3. Se possível, adicione testes automatizados

## Documentação

- Atualize o README.md se necessário
- Documente novas funcionalidades
- Adicione comentários em código complexo
- Atualize a documentação em `docs/` se aplicável

## Processo de Review

1. Todos os PRs serão revisados
2. Mantenedores podem solicitar alterações
3. Responda a comentários de forma respeitosa
4. Mantenha o PR atualizado com a branch principal

## Código de Conduta

Seja respeitoso e profissional em todas as interações. Respeite diferentes opiniões e experiências.

## Dúvidas?

Se tiver dúvidas sobre como contribuir, abra uma issue ou entre em contato com os mantenedores.

Obrigado por contribuir! 🎮

