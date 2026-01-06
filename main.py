import flet as ft
import itertools
import pandas as pd
import os
import sys
import requests
from collections import Counter

# Variável global para guardar os dados temporariamente
df_para_salvar = None

def main(page: ft.Page):
    global df_para_salvar
    
    # --- CONFIGURAÇÕES VISUAIS ---
    page.title = "Gerador Lotofácil Pro Online"
    page.window_width = 450
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"

    # --- ELEMENTOS DA TELA ---
    titulo = ft.Text("Lotofácil IA Online", size=28, weight="bold", color="blue")
    
    txt_concurso_alvo = ft.TextField(
        label="Próximo Concurso", width=150, text_align=ft.TextAlign.CENTER
    )
    txt_concurso_base = ft.TextField(
        label="Último Sorteado", width=150, text_align=ft.TextAlign.CENTER
    )
    txt_qtd_analise = ft.TextField(
        label="Analisar últimos X concursos?", value="10", width=250, 
        text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER
    )
    chk_usar_online = ft.Checkbox(label="Buscar estatísticas online", value=True)
    lbl_status = ft.Text("Pronto.", color="grey", size=14, weight="bold")
    barra_progresso = ft.ProgressBar(width=400, color="blue", bgcolor="#eeeeee", visible=False)
    lista_resultados = ft.ListView(expand=1, spacing=10, padding=20)

    # --- COMPONENTE FILE PICKER ---
    def salvar_arquivo_final(e: ft.FilePickerResultEvent):
        global df_para_salvar
        if e.path:
            try:
                df_para_salvar.to_csv(e.path, index=False, sep=';', encoding='utf-8-sig')
                lbl_status.value = f"Sucesso! Arquivo salvo."
                lbl_status.color = "green"
                page.open(ft.SnackBar(content=ft.Text(f"Arquivo salvo com sucesso!")))
            except Exception as erro:
                lbl_status.value = f"Erro ao gravar: {erro}"
                lbl_status.color = "red"
        else:
            lbl_status.value = "Salvamento cancelado."
            lbl_status.color = "orange"
        page.update()

    file_picker = ft.FilePicker(on_result=salvar_arquivo_final)
    page.overlay.append(file_picker)

    # --- FUNÇÕES AUXILIARES ---
    def fechar_app(e):
        sys.exit()

    def limpar_filtros(e=None):
        txt_concurso_alvo.value = ""
        txt_concurso_base.value = ""
        lbl_status.value = "Limpo."
        lbl_status.color = "grey"
        lista_resultados.controls.clear()
        page.update()

    def buscar_estatisticas_online(ultimo_concurso, qtd_analise):
        numeros_contados = []
        try:
            base = int(ultimo_concurso)
            qtd = int(qtd_analise)
            sucesso = 0
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'}
            
            for i in range(qtd):
                concurso_atual = base - i
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{concurso_atual}"
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        dezenas = [int(d) for d in response.json()['dezenas']]
                        numeros_contados.extend(dezenas)
                        sucesso += 1
                except:
                    continue
            
            if sucesso < 2: return None, None, "Falha Web (Poucos dados)"

            frequencia = Counter(numeros_contados)
            top_20 = sorted([num for num, freq in frequencia.most_common(20)])
            fixas = sorted([num for num, freq in frequencia.most_common(10)])
            return set(top_20), set(fixas), f"Sucesso: {sucesso} concursos."

        except Exception as e:
            return None, None, f"Erro: {str(e)}"

    # --- LÓGICA PRINCIPAL ---
    def gerar_jogos(e):
        global df_para_salvar
        lista_resultados.controls.clear()
        btn_gerar.disabled = True
        barra_progresso.visible = True
        lbl_status.value = "Processando..."
        lbl_status.color = "blue"
        page.update()

        # Validação
        if not txt_concurso_alvo.value or not txt_concurso_base.value:
            lbl_status.value = "Preencha os concursos."
            barra_progresso.visible = False
            btn_gerar.disabled = False
            page.update()
            return

        # 1. IA / Estatística (Matriz)
        pool_20, fixas = set(), set()
        info_estrategia = "Manual"
        
        if chk_usar_online.value:
            p20, fx, msg = buscar_estatisticas_online(txt_concurso_base.value, txt_qtd_analise.value)
            if p20:
                pool_20, fixas = p20, fx
                info_estrategia = f"IA Online ({msg})"
                lbl_status.value = "IA Concluída. Calculando jogos..."
            else:
                lbl_status.value = f"Erro Online: {msg}"
                pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
                fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
                info_estrategia = "OFFLINE"
        else:
            pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
            fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
            info_estrategia = "OFFLINE"

        # VISUAL 1: Exibir Matriz (VERDE)
        lista_20_ordenada = sorted(list(pool_20))
        str_20_visual = " - ".join([f"{n:02d}" for n in lista_20_ordenada])
        card_20 = ft.Container(
            content=ft.Column([
                ft.Text("MATRIZ SELECIONADA (20):", weight="bold", size=14),
                ft.Text(str_20_visual, size=18, color="green", weight="bold"),
                ft.Text(f"Fonte: {info_estrategia}", size=12, italic=True)
            ]),
            padding=15, bgcolor="green50", border=ft.border.all(1, "green"),
            border_radius=10, margin=5
        )
        lista_resultados.controls.append(card_20)

        # 2. Obter Resultado Base (Para filtro de repetidas)
        ultimo_resultado_set = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15} # Dummy padrão
        origem_base = "Fictício (Erro Online)"
        
        if chk_usar_online.value:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{txt_concurso_base.value}"
                r = requests.get(url, headers=headers, timeout=3)
                if r.status_code == 200:
                    ultimo_resultado_set = set([int(d) for d in r.json()['dezenas']])
                    origem_base = "Online (Caixa)"
            except: pass

        # VISUAL 2: Exibir Concurso Base (LARANJA - NOVO)
        lista_base_ordenada = sorted(list(ultimo_resultado_set))
        str_base_visual = " - ".join([f"{n:02d}" for n in lista_base_ordenada])
        
        card_base = ft.Container(
            content=ft.Column([
                ft.Text(f"CONCURSO BASE ({txt_concurso_base.value}):", weight="bold", size=14),
                ft.Text(str_base_visual, size=18, color="orange", weight="bold"), # Texto Laranja
                ft.Text(f"Fonte: {origem_base} | Usado para filtro de repetidas", size=12, italic=True)
            ]),
            padding=15, bgcolor="orange50", border=ft.border.all(1, "orange"),
            border_radius=10, margin=5
        )
        lista_resultados.controls.append(card_base)

        # 3. Motor Matemático
        variaveis = list(pool_20 - fixas)
        jogos_candidatos = []
        for combinacao in itertools.combinations(variaveis, 5):
            jogo_atual = fixas.union(combinacao)
            repetidas = len(jogo_atual.intersection(ultimo_resultado_set))
            primos = len(jogo_atual.intersection({2, 3, 5, 7, 11, 13, 17, 19, 23}))
            jogos_candidatos.append({'numeros': sorted(list(jogo_atual)), 'repetidas': repetidas, 'primos': primos})

        melhores_jogos = [j for j in jogos_candidatos if j['repetidas'] == 9]
        if len(melhores_jogos) < 4:
            reserva = [j for j in jogos_candidatos if j['repetidas'] in [8, 10]]
            reserva.sort(key=lambda x: abs(x['primos'] - 5))
            melhores_jogos.extend(reserva)
        jogos_finais = melhores_jogos[:5]

        # 4. Exibir Jogos Finais (AZUL)
        if not jogos_finais:
            lbl_status.value = "Nenhum jogo encontrado."
        else:
            dados_csv = []
            str_20 = ";".join([f"{n:02d}" for n in sorted(list(pool_20))])
            str_ult = ";".join([f"{n:02d}" for n in sorted(list(ultimo_resultado_set))])
            dados_csv.append({"Tipo": "Matriz", "Dezenas": str_20, "Info": info_estrategia})
            dados_csv.append({"Tipo": "Base", "Dezenas": str_ult, "Info": txt_concurso_base.value})

            for i, jogo in enumerate(jogos_finais):
                str_csv = ";".join([f"{n:02d}" for n in jogo['numeros']])
                str_vis = " - ".join([f"{n:02d}" for n in jogo['numeros']])
                dados_csv.append({"Tipo": f"Jogo {i+1}", "Dezenas": str_csv, "Info": f"R:{jogo['repetidas']}"})
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {i+1}", weight="bold"),
                        ft.Text(str_vis, size=20, color="blue"),
                        ft.Text(f"R:{jogo['repetidas']} | P:{jogo['primos']}", size=12)
                    ]), padding=10, bgcolor="blue50", border_radius=10, margin=5
                )
                lista_resultados.controls.append(card)

            # Preparar para salvar
            df_para_salvar = pd.DataFrame(dados_csv)
            lbl_status.value = "Análise pronta! Clique em Gerar para salvar se desejar."
            
            # Abre o seletor automaticamente (Opcional, se preferir clique manual remova essa linha)
            nome_sug = f"Loto_{txt_concurso_alvo.value}.csv"
            file_picker.save_file(file_name=nome_sug, allowed_extensions=["csv"])

        barra_progresso.visible = False
        btn_gerar.disabled = False
        page.update()

    # --- BOTÕES ---
    btn_gerar = ft.FilledButton("GERAR ONLINE", width=140, on_click=gerar_jogos)
    btn_limpar = ft.FilledButton("LIMPAR", width=100, style=ft.ButtonStyle(bgcolor="grey"), on_click=limpar_filtros)
    btn_sair = ft.FilledButton("SAIR", width=80, style=ft.ButtonStyle(bgcolor="red"), on_click=fechar_app)

    page.add(
        ft.Column([
            titulo,
            ft.Row([txt_concurso_alvo, txt_concurso_base], alignment=ft.MainAxisAlignment.CENTER),
            txt_qtd_analise,
            chk_usar_online,
            ft.Divider(),
            ft.Row([btn_sair, btn_limpar, btn_gerar], alignment=ft.MainAxisAlignment.CENTER),
            barra_progresso,
            lbl_status,
            lista_resultados
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)
