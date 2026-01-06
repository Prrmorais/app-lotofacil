import flet as ft
import itertools
import csv
import sys
import requests
from collections import Counter

# Variável global
dados_para_salvar = []

def main(page: ft.Page):
    global dados_para_salvar
    
    page.title = "Loto App"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400

    # --- SISTEMA DE SALVAR (Nativo) ---
    def salvar_arquivo_final(e: ft.FilePickerResultEvent):
        global dados_para_salvar
        if e.path:
            try:
                with open(e.path, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["Tipo", "Dezenas"], delimiter=';')
                    writer.writeheader()
                    writer.writerows(dados_para_salvar)
                
                lbl_status.value = "ARQUIVO SALVO!"
                lbl_status.color = "green"
                page.open(ft.SnackBar(content=ft.Text("Sucesso! Verifique a pasta.")))
            except Exception as erro:
                lbl_status.value = f"Erro: {erro}"
                lbl_status.color = "red"
        page.update()

    file_picker = ft.FilePicker(on_result=salvar_arquivo_final)
    page.overlay.append(file_picker)

    # --- UI ---
    titulo = ft.Text("Gerador Lotofácil", size=24, weight="bold", color="blue")
    txt_concurso_base = ft.TextField(label="Último Concurso", width=150, text_align="center", keyboard_type="number")
    chk_online = ft.Checkbox(label="Buscar Online", value=True)
    lbl_status = ft.Text("Pronto.", color="grey")
    lista_res = ft.ListView(expand=1, spacing=10, padding=20)

    # --- LÓGICA ---
    def processar(e):
        global dados_para_salvar
        dados_para_salvar = []
        lista_res.controls.clear()
        lbl_status.value = "Processando..."
        page.update()

        base_set = set()
        
        # Tentativa Online Simples
        if chk_online.value and txt_concurso_base.value:
            try:
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{txt_concurso_base.value}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    base_set = set([int(d) for d in r.json()['dezenas']])
            except:
                pass

        # Dummy se falhar
        if not base_set:
             base_set = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}

        # Matriz Fixa
        pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
        fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
        variaveis = list(pool_20 - fixas)
        
        # Gerar Jogos
        cont = 0
        for comb in itertools.combinations(variaveis, 5):
            jogo = fixas.union(comb)
            if len(jogo.intersection(base_set)) == 9: # Filtro 9 Repetidas
                cont += 1
                lista = sorted(list(jogo))
                str_num = "-".join([f"{n:02d}" for n in lista])
                str_csv = ";".join([f"{n:02d}" for n in lista])
                
                dados_para_salvar.append({"Tipo": f"Jogo {cont}", "Dezenas": str_csv})
                lista_res.controls.append(ft.Text(f"Jogo {cont}: {str_num}", size=16))
                
                if cont >= 5: break

        if cont == 0:
            lbl_status.value = "Nenhum jogo encontrado com 9 repetidas."
        else:
            lbl_status.value = "Sucesso! Salve o arquivo."
            # Abre salvar (nome genérico para evitar erro)
            file_picker.save_file(file_name="jogos_loto.csv", allowed_extensions=["csv"])

        page.update()

    def sair(e):
        sys.exit()

    btn_gerar = ft.FilledButton("GERAR", on_click=processar)
    btn_sair = ft.FilledButton("SAIR", on_click=sair, style=ft.ButtonStyle(bgcolor="red"))

    page.add(titulo, txt_concurso_base, chk_online, ft.Row([btn_sair, btn_gerar]), lbl_status, lista_res)

if __name__ == "__main__":
    ft.app(target=main)
