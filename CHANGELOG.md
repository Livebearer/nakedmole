# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

O formato segue a convenção [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
e este projeto adota versionamento semântico [SemVer](https://semver.org/spec/v2.0.0.html).

## [0.02.1_dev] - 2025-07-26
### Corrigido
- Corrige bug que causava erro `TclError` ao clicar em 'Editar' na janela de confirmação.
- Agora o nome editado é capturado antes da destruição da janela.
- Refatora a função `confirm_rename_gui` para garantir robustez.

## [0.02.0_dev] - 2025-07-26
### Adicionado
- Nova janela gráfica de confirmação por arquivo (modo interativo).
- Permite ver nome original, editar nome sugerido ou pular.
- Entrada com `Entry` editável e botões `OK`, `Editar`, `Pular`.
