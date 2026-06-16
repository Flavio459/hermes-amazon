# Versionamento

Utilize semver (MAJOR.MINOR.PATCH) para versionar releases deste repositório.

- **MAJOR**: Alterações incompatíveis na interface pública.
- **MINOR**: Funcionalidades novas sem quebrar compatibilidade.
- **PATCH**: Correções e ajustes.

## Branches

- `main`: Linha estável de produção.
- `develop`: Integração de novas funcionalidades antes de mesclar no `main`.
- `feature/<nome>`: Desenvolvimento isolado de novas funcionalidades.

Para lançar uma release, abra um pull request de `develop` para `main` com a tag apropriada.
