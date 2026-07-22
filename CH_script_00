import re
import sys
from pathlib import Path
import fitz  # PyMuPDF


# Tabelas de referência de furação (INFO COMB KL e INFO COMB SV)
TABELAS_FURACAO = {
    "INFO COMB KL": [
        {"dn_nome": "1/2\" (15,8mm)", "di_ref": 15.8, "min": 3.0, "max": 12.0},
        {"dn_nome": "1\" (26,2mm)", "di_ref": 26.2, "min": 3.0, "max": 20.0},
        {"dn_nome": "1.1/2\" (40,9mm)", "di_ref": 40.9, "min": 3.0, "max": 32.0},
        {"dn_nome": "2\" (52,5mm)", "di_ref": 52.5, "min": 3.0, "max": 40.0},
    ],
    "INFO COMB SV": [
        {"dn_nome": "1/2\" (15,8mm)", "di_ref": 15.8, "min": 2.6, "max": 12.9},
        {"dn_nome": "1\" (26,2mm)", "di_ref": 26.2, "min": 2.6, "max": 23.8},
        {"dn_nome": "1.1/2\" (40,9mm)", "di_ref": 40.9, "min": 2.6, "max": 36.0},
        {"dn_nome": "2\" (52,5mm)", "di_ref": 52.5, "min": 2.6, "max": 46.4},
        {"dn_nome": "2.1/2\" (62,7mm)", "di_ref": 62.7, "min": 2.6, "max": 53.5},
    ],
}

LIMITES = {
    "Klents FK-5112": {
        "Two-phase discharge time": {"min": 3.0, "max": 10.0, "recomendado": 8.0},
        "Concentração de extinção": {"fixo": 3.3},
        "Fator de Projeto Classe C": {"min": 1.35},
        "Concentração de agente após a descarga": {"min": 4.5},
        "Pressão no difusor": {"min": 5.0},
        "furacao_tabela_referencia": "INFO COMB KL",
    },
    "HFC-227ea": {
        "Two-phase discharge time": {"min": 3.0, "max": 10.0, "recomendado": 8.0},
        "Concentração de extinção": {"fixo": 5.2},
        "Fator de Projeto Classe C": {"min": 1.35},
        "Concentração de agente após a descarga": {"min": 7.0},
        "Pressão no difusor": {"min": 5.0},
        "furacao_tabela_referencia": "INFO COMB KL",
    },
    "Sevo FK-5112": {
        "Two-phase discharge time": {"min": 3.0, "max": 9.9, "recomendado": 8.0},
        "Concentração de extinção": {"fixo": 3.3},
        "Fator de Projeto Classe C": {"min": 1.35},
        "Concentração de agente após a descarga": {"min": 4.5},
        "Pressão no difusor": {"min": 5.0},
        "altitude_cabecario_m": {"fixo": 0.0},
        "furacao_tabela_referencia": "INFO COMB SV",
    },
}

ALIASES = {
    "Klents FK-5112": [r"FK-5-1-12"],
    "HFC-227ea": [r"HFC-?227\s*ea"],
    "Sevo FK-5112": [r"SEVO\s*SYSTEMS", r"\bNovec\b"],
}

TEXTO_ERRO_ALVO = "PRESCRIBED CONCENTRATION-DISTRIBUTION IN THE ZONES ARE NOT GUARANTEED"

# Leitura e Extração
def ler_texto_pdf(caminho_pdf: str) -> str:
    import shutil
    import subprocess

    if shutil.which("pdftotext"):
        resultado = subprocess.run(
            ["pdftotext", "-layout", caminho_pdf, "-"],
            capture_output=True, text=True, check=True,
        )
        return resultado.stdout

    import pdfplumber
    partes = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            partes.append(pagina.extract_text() or "")
    return "\n".join(partes)


def detectar_agente(texto: str):
    for nome_agente, aliases in ALIASES.items():
        for alias in aliases:
            if re.search(alias, texto, flags=re.IGNORECASE):
                return nome_agente
    return None


def _float(valor_str):
    if valor_str is None:
        return None
    try:
        s = valor_str.strip().replace(".", "").replace(",", ".") if "," in valor_str else valor_str.strip()
        return float(s)
    except (TypeError, ValueError):
        return None


def checar_mensagem_erro_pag1(caminho_pdf: str) -> bool:
    try:
        doc = fitz.open(caminho_pdf)
        if len(doc) > 0:
            texto_p1 = doc[0].get_text()
            return TEXTO_ERRO_ALVO in texto_p1
    except Exception:
        pass
    return False


def extrair_altitude_sevo(texto: str):
    m = re.search(r"Altitude\s+above\s+sealevel:\s*([\d,.]+)\s*m", texto, re.IGNORECASE)
    return _float(m.group(1)) if m else None


def extrair_tempo_descarga_bifasico(texto: str):
    m = re.search(r"Two-?phase\s+discharge\s+time:\s*([\d,.]+)\s*s", texto, re.IGNORECASE)
    return _float(m.group(1)) if m else None


def extrair_zonas(texto: str):
    inicio = re.search(r"Calculation\s+of\s+design\s+quantity:", texto, re.IGNORECASE)
    if not inicio:
        return []
    resto = texto[inicio.end():]
    fim = re.search(r"Regulation\s+rule\s+for\s+calculation", resto, re.IGNORECASE)
    bloco = resto[: fim.start() if fim else len(resto)]

    zonas = []
    linhas = bloco.splitlines()
    for linha in linhas:
        m_nums = re.findall(r"\d+,\d+", linha)
        if len(m_nums) >= 4:
            zonas.append({
                "volume_building_parts": _float(m_nums[1]) if len(m_nums) >= 6 else 0.0,
                "extinguish_conc": _float(m_nums[-4]),
                "design_factor": _float(m_nums[-3]),
                "design_conc": _float(m_nums[-2]),
                "design_quantity": _float(m_nums[-1]),
            })
    return zonas


def extrair_pressoes_nozzles(texto: str):
    inicio = re.search(r"Pipe\s+system:", texto, re.IGNORECASE)
    if not inicio:
        return []
    resto = texto[inicio.end():]
    fim = re.search(r"Nozzle\s+data:", resto, re.IGNORECASE)
    bloco = resto[: fim.start() if fim else len(resto)]

    pressoes = []
    padrao = re.compile(r"^\s*\d+\s+\d+\s+(\d{4,})\s+([\d,.]+)", re.MULTILINE)
    for m in padrao.finditer(bloco):
        pressao = _float(m.group(2))
        if pressao is not None:
            pressoes.append(pressao)
    return pressoes


def extrair_detalhes_nozzles(texto: str):
    pipe_di = {}
    inicio_pipe = re.search(r"Pipe\s+system:", texto, re.IGNORECASE)
    if inicio_pipe:
        bloco_pipe = texto[inicio_pipe.end():]
        fim_pipe = re.search(r"Nozzle\s+data:", bloco_pipe, re.IGNORECASE)
        bloco_pipe = bloco_pipe[: fim_pipe.start() if fim_pipe else len(bloco_pipe)]
        
        padrao_pipe = re.compile(r"^\s*\d+\s+\d+\s+(\d{4,})\s+[\d,.]+\s+[\d,.]+\s+([\d,.]+)", re.MULTILINE)
        for m in padrao_pipe.finditer(bloco_pipe):
            nid = m.group(1)
            di_mm = float(m.group(2).replace(",", "."))
            pipe_di[nid] = di_mm

    inicio_noz = re.search(r"Nozzle\s+data:", texto, re.IGNORECASE)
    if not inicio_noz:
        return []

    resto_noz = texto[inicio_noz.end():]
    fim_noz = re.search(r"Legend\s+of\s+nozzles|Two-phase\s+discharge\s+time|MAXIMUM\s+TRANSPORT", resto_noz, re.IGNORECASE)
    bloco_noz = resto_noz[: fim_noz.start() if fim_noz else len(resto_noz)]

    nozzles = []
    linhas = bloco_noz.splitlines()
    for linha in linhas:
        m_id = re.search(r"\b(\d{4,})\b", linha)
        if m_id:
            nid = m_id.group(1)
            nums = re.findall(r"\d+[\.,]\d+", linha)
            if nums:
                orifice = float(nums[-1].replace(",", "."))
                di_mm = pipe_di.get(nid, 26.2)
                nozzles.append({"id": nid, "di_mm": di_mm, "orifice_mm": orifice})

    if not nozzles:
        matches = list(re.finditer(r"\b(\d{4,})\b", bloco_noz))
        for i, m in enumerate(matches):
            nid = m.group(1)
            sub_str = bloco_noz[m.start(): matches[i + 1].start() if i + 1 < len(matches) else len(bloco_noz)]
            nums = re.findall(r"\d+[\.,]\d+", sub_str)
            if nums:
                orifice = float(nums[0].replace(",", "."))
                di_mm = pipe_di.get(nid, 26.2)
                nozzles.append({"id": nid, "di_mm": di_mm, "orifice_mm": orifice})

    return nozzles


def extrair_tubulacoes(texto: str):
    smooth = bool(re.search(r"SCHEDULE\s*40.*smooth", texto, re.IGNORECASE | re.DOTALL))
    galvanized = bool(re.search(r"SCHEDULE\s*40.*galvanized", texto, re.IGNORECASE | re.DOTALL))
    return {"schedule40_smooth": smooth, "schedule40_galvanized": galvanized}


# Validação de Parâmetros
def validar_numero(valor, regras: dict):
    if valor is None:
        return "NÃO ENCONTRADO NO PDF", ""

    if "fixo" in regras:
        if abs(valor - regras["fixo"]) < 1e-4:
            return "OK", ""
        return "DIVERGENTE DO ESPERADO", f"esperado: {regras['fixo']}"

    status, detalhes = "OK", []
    if "min" in regras and valor < regras["min"]:
        status = "ABAIXO DO MÍNIMO"
        detalhes.append(f"mínimo: {regras['min']}")
    if "max" in regras and valor > regras["max"]:
        status = "ACIMA DO MÁXIMO"
        detalhes.append(f"máximo: {regras['max']}")
    if "recomendado" in regras and status == "OK":
        detalhes.append(f"recomendado: {regras['recomendado']}")
    return status, "; ".join(detalhes)


def validar_furacao_nozzles_tabela(nozzles, ref_tabela):
    tabela = TABELAS_FURACAO.get(ref_tabela, [])
    if not nozzles or not tabela:
        return {
            "status": "NÃO ENCONTRADO",
            "qtd": 0,
            "linhas": []
        }

    linhas = []
    tem_erro = False

    for n in nozzles:
        # Encontra a bitola/DN mais próxima com base no diâmetro da tubulação (di_mm)
        lim = min(tabela, key=lambda x: abs(x["di_ref"] - n["di_mm"]))
        orf = n["orifice_mm"]
        min_mm = lim["min"]
        max_mm = lim["max"]

        if orf < min_mm or orf > max_mm:
            st = "NOK"
            tem_erro = True
        else:
            st = "OK"

        linhas.append({
            "bico": n["id"],
            "dn": lim["dn_nome"].split()[0],  # Pega apenas o DN (ex: 1/2", 1", 2")
            "tam": f"{orf:.1f} mm",
            "min": f"{min_mm:.1f} mm",
            "max": f"{max_mm:.1f} mm",
            "status": f"[{st}]"
        })

    return {
        "status": "REPROVADO" if tem_erro else "OK",
        "qtd": len(nozzles),
        "linhas": linhas
    }


def definir_status_geral(campos: dict, tabela_furacao: dict) -> str:
    status_invalidos = [
        "ABAIXO DO MÍNIMO", "ACIMA DO MÁXIMO", "DIVERGENTE DO ESPERADO",
        "FORA DOS LIMITES", "NÃO ENCONTRADO", "VERIFICAR MANUALMENTE"
    ]
    for info in campos.values():
        if info["status"] in status_invalidos:
            return "REPROVADO"
            
    if tabela_furacao.get("status") in ["REPROVADO", "NÃO ENCONTRADO"]:
        return "REPROVADO"

    return "APROVADO"


def analisar_pdf(caminho_pdf: str) -> dict:
    texto = ler_texto_pdf(caminho_pdf)
    agente = detectar_agente(texto)
    if not agente:
        return {"agente": None, "status_geral": "REPROVADO", "tem_erro_pag1": False}

    regras = LIMITES[agente]
    zonas = extrair_zonas(texto)
    pressoes_nozzles = extrair_pressoes_nozzles(texto)
    nozzles_detalhes = extrair_detalhes_nozzles(texto)
    tubulacoes = extrair_tubulacoes(texto)

    resultado = {"agente": agente, "campos": {}}

    # Two-phase discharge time
    tempo = extrair_tempo_descarga_bifasico(texto)
    status, detalhe = validar_numero(tempo, regras["Two-phase discharge time"])
    resultado["campos"]["Two-phase discharge time"] = {
        "valor": f"{tempo} s" if tempo else None, "status": status, "detalhe": detalhe,
    }

    # Concentrações e Fator de Projeto
    if zonas:
        extinguish = zonas[0]["extinguish_conc"]
        factor_pior = min(z["design_factor"] for z in zonas if z["design_factor"] is not None)
        conc_pior = min(z["design_conc"] for z in zonas if z["design_conc"] is not None)
    else:
        extinguish = factor_pior = conc_pior = None

    status, detalhe = validar_numero(extinguish, regras["Concentração de extinção"])
    resultado["campos"]["Concentração de extinção"] = {
        "valor": f"{extinguish}%" if extinguish else None, "status": status, "detalhe": detalhe,
    }

    status, detalhe = validar_numero(factor_pior, regras["Fator de Projeto Classe C"])
    resultado["campos"]["Fator de Projeto Classe C"] = {
        "valor": factor_pior, "status": status, "detalhe": detalhe,
    }

    status, detalhe = validar_numero(conc_pior, regras["Concentração de agente após a descarga"])
    resultado["campos"]["Concentração de agente após a descarga"] = {
        "valor": f"{conc_pior}%" if conc_pior else None, "status": status, "detalhe": detalhe,
    }

    # Pressão no difusor
    pressao_pior = min(pressoes_nozzles) if pressoes_nozzles else None
    status, detalhe = validar_numero(pressao_pior, regras["Pressão no difusor"])
    resultado["campos"]["Pressão no difusor"] = {
        "valor": f"{pressao_pior} bar" if pressao_pior else None, "status": status, "detalhe": detalhe,
    }

    # Tubulações
    resultado["campos"]["Tubulação interna ao cilindro"] = {
        "valor": "Schedule 40 Smooth" if tubulacoes["schedule40_smooth"] else None,
        "status": "OK" if tubulacoes["schedule40_smooth"] else "NÃO ENCONTRADO",
        "detalhe": "esperado: Schedule 40 Smooth",
    }

    resultado["campos"]["Tubulação externa"] = {
        "valor": "Schedule 40 Galvanized" if tubulacoes["schedule40_galvanized"] else None,
        "status": "OK" if tubulacoes["schedule40_galvanized"] else "NÃO ENCONTRADO",
        "detalhe": "esperado: Schedule 40 Galvanized",
    }

    # Altitude e Desconto (Sevo FK-5112)
    if "altitude_cabecario_m" in regras:
        altitude = extrair_altitude_sevo(texto)
        status, detalhe = validar_numero(altitude, regras["altitude_cabecario_m"])
        resultado["campos"]["Altitude no cabeçário"] = {
            "valor": f"{altitude} m" if altitude is not None else None, "status": status, "detalhe": detalhe,
        }

        tem_desconto = any(z["volume_building_parts"] > 0 for z in zonas)
        resultado["campos"]["Desconto de altitude via volume building parts"] = {
            "valor": "Aplicado nas zonas" if tem_desconto else "Não aplicado em nenhuma zona",
            "status": "OK" if tem_desconto else "VERIFICAR MANUALMENTE",
            "detalhe": "desconto deve estar na coluna 'Volume of building parts'",
        }

    # Tabela de Furação
    resultado["tabela_furacao"] = validar_furacao_nozzles_tabela(
        nozzles_detalhes, regras["furacao_tabela_referencia"]
    )

    resultado["status_geral"] = definir_status_geral(resultado["campos"], resultado["tabela_furacao"])
    resultado["tem_erro_pag1"] = checar_mensagem_erro_pag1(caminho_pdf)

    return resultado


def remover_mensagem_erro_pdf(caminho_origem: str, caminho_destino: str) -> bool:
    try:
        doc = fitz.open(caminho_origem)
        if len(doc) > 0:
            pagina = doc[0]
            retangulos = []

            termos_busca = [
                "!!!",
                "PRESCRIBED CONCENTRATION-DISTRIBUTION IN THE ZONES ARE NOT GUARANTEED",
                "Error messages:",
            ]

            for termo in termos_busca:
                encontrados = pagina.search_for(termo)
                retangulos.extend(encontrados)

            if retangulos:
                for rect in retangulos:
                    rect_expandido = fitz.Rect(
                        rect.x0 - 3, rect.y0 - 2, rect.x1 + 3, rect.y1 + 2
                    )
                    pagina.add_redact_annot(rect_expandido, fill=(1, 1, 1))

                pagina.apply_redactions()

            doc.save(caminho_destino)
            return True
    except Exception as e:
        print(f"Erro ao remover mensagem do PDF: {e}")
    return False
