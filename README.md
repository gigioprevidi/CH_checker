# 🛡️ CH CHECKER - Auditor de Cálculos Hidráulicos (Agente Limpo)

O **CH CHECKER** é uma aplicação desktop desenvolvida em Python para automação da auditoria e verificação de relatórios de Cálculo Hidráulico (sistemas de combate a incêndio por agentes limpos: **Klents FK-5112**, **HFC-227ea** e **Sevo FK-5112**).

A ferramenta extrai os parâmetros técnicos diretamente de relatórios em PDF, valida cada parâmetro com base em normas e tabelas de referência e permite a remoção automática de mensagens de aviso da primeira página para relatórios aprovados.

---

## 🚀 Funcionalidades

- 📄 **Análise Automática de PDFs:** Leitura inteligente do relatório extraindo agentes, tempos de descarga, pressões, vazões e tubulações.
- 📐 **Validação de Furação de Difusores:** Tabela interativa que mapeia o nó do bico, identifica o diâmetro nominal (**DN**) da tubulação e valida se o diâmetro da furação (**TAM BICO**) está dentro dos limites mínimo (**TAM MIN**) e máximo (**TAM MAX**).
- ⚙️ **Suporte Multi-Agente:**
  - **Klents FK-5112** *(Tabela INFO COMB KL)*
  - **HFC-227ea** *(Tabela INFO COMB KL)*
  - **Sevo FK-5112** *(Tabela INFO COMB SV - validação de altitude e desconto)*
- 🧹 **Edição e Limpeza de PDF:** Identifica a mensagem de erro da página 1 (`!!! PRESCRIBED CONCENTRATION-DISTRIBUTION IN THE ZONES ARE NOT GUARANTEED`) e habilita um botão dinâmico para gerar uma cópia limpa do PDF aprovado.
- 🖥️ **Interface Gráfica Simples (Tkinter):** Visualização instantânea do resultado com tabela alinhada e status geral (**APROVADO** / **REPROVADO**).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **[Tkinter](https://docs.python.org/3/library/tkinter.html):** Interface gráfica nativa.
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/):** Manipulação, busca e aplicação de redação (limpeza de mensagens) no PDF.
- **[pdfplumber](https://github.com/jsvine/pdfplumber):** Extração de texto em PDFs com layout complexo.
- **[PyInstaller](https://pyinstaller.org/):** Compilação do script para executável `.exe` independente.

---

## 📂 Estrutura do Projeto

```text
├── CH_script_00.py    # Módulo de extração, regras de negócio e validação dos PDFs
├── CH_00.py      # Interface gráfica (Tkinter) e fluxo do aplicativo
├── README.md              # Documentação do projeto
└── dist/
    └── CH_00.exe     # Executável gerado para distribuição
