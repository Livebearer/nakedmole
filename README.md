# PDF Renamer

Renomeador automatizado de arquivos PDF com base em metadados (título, autor, ano) e interface gráfica em Python.

## Funcionalidades

- Extração de metadados usando `PyPDF2`, com fallback por leitura bruta.
- Renomeação interativa com janela de confirmação (editar, aceitar, pular).
- Evita sobrescrever arquivos (gera nomes únicos).
- Geração de relatório `read.me` com histórico das alterações.
- Suporte a interface gráfica com `tkinter`.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas:
  - PyPDF2
  - tkinter (incluso na instalação padrão do Python)

## Como usar

1. Execute o script:
   ```bash
   python pdf_renamer_0.02.1_dev.py
   ```

2. Selecione a pasta contendo arquivos PDF.

3. Escolha os arquivos a renomear, revise ou edite os nomes sugeridos.

## Histórico de versões

Veja [CHANGELOG.md](./CHANGELOG.md)

## Licença

Este projeto está sob a licença MIT.

## Autor

Livebearer
