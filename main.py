import flet as ft
import itertools
import csv  # Substitui o Pandas (Nativo e Leve)
import os
import sys
import requests
from collections import Counter

# Variável global para guardar os dados na memória (Lista de Dicionários)
dados_para_salvar = []

def main(page: ft.Page):
    global dados_para_salvar
    
    # Configurações para evitar travamentos
    page.title = "Loto Leve"
    page.window_width = 400
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"

    # --- COMPONENTE DE SALVAR (FILE PICKER) ---
    def salvar_arquivo_final(e: ft.FilePickerResultEvent):
        global dados_para_salvar
        if e.path:
            try:
                # Lógica nativa do Python para criar CSV (Sem Pandas)
                with open(e.path, mode='w', newline='', encoding='utf-8-sig') as f:
                    # Define as colunas
                    writer = csv.DictWriter(f, fieldnames=["Tipo", "Dezenas", "Info"], delimiter=';')
                    writer.writeheader()
                    # Escreve as linhas
                    writer.writerows(dados_para_salvar)
                
                lbl_status.value = "ARQUIVO SALVO COM SUCESSO!"
                lbl_status.color = "green"
                page.open(ft.SnackBar(content=ft.Text("Sucesso! Verifique a pasta.")))
                
            except Exception as erro:
                lbl_status.value = f"Erro de gravação: {erro}"
                lbl_status.color = "red"
        else:
            lbl_status.value = "Salvamento cancelado."
        page.update()

    file_picker = ft.FilePicker(on_result=salvar_arquivo_final)
    page.overlay.append(file_picker)

    # --- UI SIMPLIFICADA ---
    titulo = ft.Text("Lotofácil Leve & Rápida", size=24, weight="bold", color="blue")
    
    txt_concurso_base = ft.TextField(label="Último Concurso (Base)", width=180, text_align="center", keyboard_type="number")
    txt_concurso_alvo = ft.TextField(label="Próximo Concurso", width=180, text_align="center", keyboard_type="number")
    
    chk_online = ft.Checkbox(label="Buscar Online (Recomendado)", value=True)
    lbl_status = ft.Text("Pronto.", color="grey")
    
    lista_res = ft.ListView(expand=1, spacing=10, padding=20)

    # --- LÓGICA DE NEGÓCIO ---
    def processar(e):
        global dados_para_salvar
        dados_para_salvar = [] # Limpa memória
        lista_res.controls.clear()
        
        lbl_status.value = "Processando..."
        lbl_status.color = "blue"
        page.update()

        # 1. Obter Base (Online ou Manual)
        base_set = set()
        fonte_info = "Manual/Padrão"
        
        if chk_online.value and txt_concurso_base.value:
            try:
                # Tenta baixar APENAS o último resultado (Mais rápido)
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{txt_concurso_base.value}"
                r = requests.get(url, timeout=4)
                if r.status_code == 200:
                    base_set = set([int(d) for d in r.json()['dezenas']])
                    fonte_info = "Online (API)"
            except:
                fonte_info = "Falha Online (Usando Dummy)"

        # Se falhou ou não tem internet, usa um dummy para não travar
        if not base_set:
             base_set = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}

        # 2. Matriz Fixa (Para garantir leveza e rapidez hoje)
        pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
        fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
        
        # 3. Gerar Jogos
        variaveis = list(pool_20 - fixas)
        jogos_validos = []
        
        for comb in itertools.combinations(variaveis, 5):
            jogo = fixas.union(comb)
            # Filtro Repetidas
            repetidas = len(jogo.intersection(base_set))
            
            if repetidas == 9: # Filtro Rígido
                jogos_validos.append(sorted(list(jogo)))

        # Pega só os 5 primeiros para não encher a tela
        finais = jogos_validos[:5]
        
        if not finais:
            lbl_status.value = "Nenhum jogo com 9 repetidas encontrado na matriz."
            lbl_status.color = "orange"
        else:
            # Prepara dados para o CSV
            str_base = ";".join([f"{n:02d}" for n in sorted(list(base_set))])
            dados_para_salvar.append({"Tipo": "Base", "Dezenas": str_base, "Info": fonte_info})

            for i, j in enumerate(finais):
                str_num = ";".join([f"{n:02d}" for n in j])
                str_vis = " - ".join([f"{n:02d}" for n in j])
                
                # Adiciona na lista de salvar
                dados_para_salvar.append({"Tipo": f"Jogo {i+1}", "Dezenas": str_num, "Info": "R:9"})
                
                # Adiciona na tela
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {i+1}", weight="bold"),
                        ft.Text(str_vis, size=18, color="blue")
                    ]),
                    padding=10, bgcolor="blue50", border_radius=8
                )
                lista_res.controls.append(card)

            lbl_status.value = "Análise concluída. Salve o arquivo."
            lbl_status.color = "green"
            
            # Abre janela de salvar
            file_picker.save_file(file_name=f"Loto_{txt_concurso_alvo.value}.csv", allowed_extensions=["csv"])

        page.update()

    def sair(e):
        sys.exit()

    # Botões
    btn_gerar = ft.FilledButton("GERAR JOGOS", on_click=processar, width=200)
    btn_sair = ft.FilledButton("SAIR", on_click=sair, style=ft.ButtonStyle(bgcolor="red"))

    page.add(
        ft.Column([
            titulo,
            txt_concurso_base,
            txt_concurso_alvo,
            chk_online,
            ft.Row([btn_sair, btn_gerar], alignment="center"),
            lbl_status,
            lista_res
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main)
