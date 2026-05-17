# Contribuindo para o Terminal Radar B3

Este documento descreve como contribuir com o projeto e quais são as práticas recomendadas para alterações.

## Como contribuir

1. Fork ou clone o repositório.
2. Crie uma branch com nome descritivo, por exemplo:

```bash
git checkout -b feature/documentacao
```

3. Faça alterações pequenas e focadas.
4. Adicione uma descrição clara no commit.
5. Envie um pull request para `main`.

## Convenções de documentação

- Atualize `README.md` quando houver mudanças de uso ou arquitetura.
- Use `docs/` para documentação técnica adicional.
- Mantenha os arquivos de documentação claros e objetivos.

## Sugestões de melhoria

- Adicionar persistência de carteira no backend.
- Criar testes automatizados para as rotas Express.
- Melhorar a validação de entrada do ticker e das datas.
- Adicionar CI para rodar lint e testes antes do merge.

## Observações

- Evite alterar arquivos grandes de dados sem necessidade.
- Se precisar alterar `estrutura_b3_completa.json`, mantenha o formato de objeto por categoria.
- Prefira comentários em português claro e conciso.
