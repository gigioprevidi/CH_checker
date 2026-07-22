import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from CH_script import analisar_pdf, remover_mensagem_erro_pdf


caminho_pdf_atual = None


def gerar_pdf_sem_erro():
    global caminho_pdf_atual
    if not caminho_pdf_atual:
        return

    path_origem = Path(caminho_pdf_atual)
    sugerido = path_origem.parent / f"{path_origem.stem}_SEM_ERRO.pdf"

    caminho_salvar = filedialog.asksaveasfilename(
        title="Salvar PDF Sem Mensagem de Erro",
        initialfile=sugerido.name,
        defaultextension=".pdf",
        filetypes=[("Arquivos PDF", "*.pdf")],
    )

    if caminho_salvar:
        sucesso = remover_mensagem_erro_pdf(caminho_pdf_atual, caminho_salvar)
        if sucesso:
            messagebox.showinfo(
                "Sucesso", f"Novo PDF gerado com sucesso!\nSalvo em:\n{caminho_salvar}"
            )
        else:
            messagebox.showerror("Erro", "Não foi possível gerar o novo PDF.")


def selecionar_e_analisar():
    global caminho_pdf_atual

    caminho_pdf = filedialog.askopenfilename(
        title="Selecione o PDF de Cálculo Hidráulico",
        filetypes=[("Arquivos PDF", "*.pdf")],
    )

    if not caminho_pdf:
        return

    caminho_pdf_atual = caminho_pdf
    lbl_arquivo.config(text=f"Arquivo: {Path(caminho_pdf).name}")
    txt_resultado.delete("1.0", tk.END)
    txt_resultado.insert(tk.END, "Analisando parâmetros do PDF, aguarde...\n")
    btn_limpar_erro.pack_forget()
    root.update()

    try:
        resultado = analisar_pdf(caminho_pdf)
        status = resultado.get("status_geral", "REPROVADO")
        agente = resultado.get("agente", "Não identificado")
        tem_erro_p1 = resultado.get("tem_erro_pag1", False)

        txt_resultado.delete("1.0", tk.END)

        if status == "APROVADO":
            lbl_status.config(text="STATUS FINAL: APROVADO", fg="green")
            if tem_erro_p1:
                btn_limpar_erro.pack(in_=frame_botoes, side=tk.LEFT, padx=5)
        else:
            lbl_status.config(text="STATUS FINAL: REPROVADO", fg="red")

        txt_resultado.insert(tk.END, f"Agente Detectado: {agente}\n")
        if tem_erro_p1:
            txt_resultado.insert(
                tk.END, "⚠️ Mensagem de erro detectada na Pág 1.\n"
            )
        txt_resultado.insert(tk.END, "=" * 65 + "\n\n")

        # Exibe os parâmetros gerais
        for campo, info in resultado.get("campos", {}).items():
            valor = info["valor"] if info["valor"] is not None else "-"
            st = info["status"]
            det = f" ({info['detalhe']})" if info["detalhe"] else ""
            txt_resultado.insert(
                tk.END, f"• {campo}:\n  Valor: {valor} | Status: [{st}]{det}\n\n"
            )

        # Exibe a Tabela de Furação dos Difusores
        # Exibe a Tabela de Furação dos Difusores
        fur_data = resultado.get("tabela_furacao", {})
        st_fur = fur_data.get("status", "-")
        qtd_fur = fur_data.get("qtd", 0)

        txt_resultado.insert(tk.END, "=" * 70 + "\n")
        txt_resultado.insert(tk.END, "FURAÇÃO\n")
        txt_resultado.insert(tk.END, f"Quantidade: {qtd_fur} bicos | Status : [{st_fur}]\n")
        txt_resultado.insert(
            tk.END, f"{'N BICO':<10} | {'DN':<8} | {'TAM BICO':<10} | {'TAM MIN':<10} | {'TAM MAX':<10} |\n"
        )
        txt_resultado.insert(tk.END, "-" * 70 + "\n")

        linhas = fur_data.get("linhas", [])
        if linhas:
            for l in linhas:
                txt_resultado.insert(
                    tk.END,
                    f"{l['bico']:<10} | {l['dn']:<8} | {l['tam']:<10} | {l['min']:<10} | {l['max']:<10} | {l['status']}\n",
                )
        else:
            txt_resultado.insert(tk.END, "Nenhum bico encontrado no PDF.\n")

        txt_resultado.insert(tk.END, "=" * 70 + "\n\n")

    except Exception as e:
        lbl_status.config(text="ERRO AO PROCESSAR", fg="orange")
        txt_resultado.delete("1.0", tk.END)
        txt_resultado.insert(
            tk.END, f"Ocorreu um erro ao processar o PDF:\n{e}"
        )


# ---------------------------------------------------------------------------
# Interface Gráfica
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("Cálculo Hidráulico R00")
root.geometry("800x640")

frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=15)

btn_selecionar = tk.Button(
    frame_botoes,
    text="📁 Selecionar e Validar PDF",
    font=("Arial", 11, "bold"),
    bg="#0275d8",
    fg="white",
    padx=10,
    pady=8,
    command=selecionar_e_analisar,
)
btn_selecionar.pack(side=tk.LEFT, padx=5)

btn_limpar_erro = tk.Button(
    frame_botoes,
    text="🧹 Gerar PDF sem mensagem de erro",
    font=("Arial", 11, "bold"),
    bg="#5cb85c",
    fg="white",
    padx=10,
    pady=8,
    command=gerar_pdf_sem_erro,
)

lbl_arquivo = tk.Label(
    root, text="Nenhum arquivo selecionado.", font=("Arial", 9, "italic")
)
lbl_arquivo.pack()

lbl_status = tk.Label(root, text="STATUS FINAL: -", font=("Arial", 16, "bold"))
lbl_status.pack(pady=10)

txt_resultado = scrolledtext.ScrolledText(
    root, width=88, height=22, font=("Consolas", 9)
)
txt_resultado.pack(padx=15, pady=10)

root.mainloop()
