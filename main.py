import flet as ft
import itertools
import pandas as pd
import os
import sys
import requests
from collections import Counter

def main(page: ft.Page):
    # --- CONFIGURAÇÕES VISUAIS ---
    page.title = "Gerador Lotofácil Pro Online"
    page.window_width = 450
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"

    # --- ELEMENTOS DA TELA ---
    
    titulo = ft.Text("Lotofácil IA Online", size=28, weight="bold", color="blue")
    
    txt_concurso_alvo = ft.TextField(
        label="Próximo Concurso", 
        width=150, 
        text_align=ft.TextAlign.CENTER
    )

    txt_concurso_base = ft.TextField(
        label="Último Sorteado", 
        width=150, 
        text_align=ft.TextAlign.CENTER
    )

    txt_qtd_analise = ft.TextField(
        label="Analisar últimos X concursos?",
        value="10",
        width=250,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    chk_usar_online = ft.Checkbox(label="Buscar estatísticas online", value=True)

    lbl_status = ft.Text("Pronto.", color="grey", size=14, weight="bold")
    
    barra_progresso = ft.ProgressBar(width=400, color="blue", bgcolor="#eeeeee", visible=False)
    
    lista_resultados = ft.ListView(expand=1, spacing=10, padding=20)

    # --- FUNÇÕES ---

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
        """Busca online disfarçando-se de navegador"""
        numeros_contados = []
        erros_detalhes = []
        
        try:
            base = int(ultimo_concurso)
            qtd = int(qtd_analise)
            sucesso = 0
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for i in range(qtd):
                concurso_atual = base - i
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{concurso_atual}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        dados = response.json()
                        dezenas = [int(d) for d in dados['dezenas']]
                        numeros_contados.extend(dezenas)
                        sucesso += 1
                    else:
                        erros_detalhes.append(f"C{concurso_atual}:Status {response.status_code}")
                except Exception as e:
                    erros_detalhes.append(f"C{concurso_atual}:Erro Conexão")
                    continue
                
            if sucesso < 2:
                msg_erro = " | ".join(erros_detalhes[:3])
                return None, None, f"Falha Web: {msg_erro}"

            frequencia = Counter(numeros_contados)
            top_20 = sorted([num for num, freq in frequencia.most_common(20)])
            fixas = sorted([num for num, freq in frequencia.most_common(10)])
            
            msg = f"Sucesso: {sucesso} concursos analisados."
            return set(top_20), set(fixas), msg

        except Exception as e:
            return None, None, f"Erro Crítico: {str(e)}"

    # --- LÓGICA PRINCIPAL ---
    def gerar_jogos(e):
        lista_resultados.controls.clear()
        btn_gerar.disabled = True
        barra_progresso.visible = True
        lbl_status.value = "Conectando... (Pode demorar 10s)"
        lbl_status.color = "blue"
        page.update()

        # 1. Pasta
        try:
            if page.platform == ft.PagePlatform.ANDROID:
                caminho_pasta = "/storage/emulated/0/Download"
            else:
                caminho_pasta = r"D:\Phyton\Lotofacil"
            
            if page.platform != ft.PagePlatform.ANDROID and not os.path.exists(caminho_pasta):
                os.makedirs(caminho_pasta)
        except Exception as erro:
            lbl_status.value = f"Erro de Permissão na Pasta: {erro}"
            lbl_status.color = "red"
            barra_progresso.visible = False
            btn_gerar.disabled = False
            page.update()
            return

        # 2. Validação
        if not txt_concurso_alvo.value or not txt_concurso_base.value:
            lbl_status.value = "ERRO: Preencha os campos de concurso."
            lbl_status.color = "red"
            barra_progresso.visible = False
            btn_gerar.disabled = False
            page.update()
            return

        # 3. Busca Inteligente
        pool_20 = set()
        fixas = set()
        info_estrategia = "Manual"
        ultimo_resultado_set = set()

        if chk_usar_online.value:
            p20, fx, msg = buscar_estatisticas_online(txt_concurso_base.value, txt_qtd_analise.value)
            
            if p20:
                pool_20 = p20
                fixas = fx
                info_estrategia = f"IA Online ({msg})"
                lbl_status.value = f"Online OK! {msg}"
            else:
                lbl_status.value = f"ERRO ONLINE: {msg}"
                lbl_status.color = "red"
                # Padrão
                pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
                fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
                info_estrategia = "OFFLINE (Falha na conexão)"
        else:
            pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
            fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
            info_estrategia = "Modo Offline Manual"

        # --- EXIBIÇÃO DAS 20 DEZENAS SELECIONADAS (NOVO) ---
        lista_20_ordenada = sorted(list(pool_20))
        str_20_visual = " - ".join([f"{n:02d}" for n in lista_20_ordenada])
        
        card_20 = ft.Container(
            content=ft.Column([
                ft.Text("MATRIZ DE 20 DEZENAS SELECIONADA:", weight="bold", color="black", size=14),
                ft.Text(str_20_visual, size=18, color="green", weight="bold"),
                ft.Text(f"Fonte: {info_estrategia}", size=12, color="grey", italic=True)
            ]),
            padding=15,
            bgcolor="green50", # Cor verde claro para destacar
            border=ft.border.all(1, "green"),
            border_radius=10,
            margin=5
        )
        lista_resultados.controls.append(card_20)
        # ----------------------------------------------------

        # Tenta pegar último resultado para repetidas
        if chk_usar_online.value:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{txt_concurso_base.value}"
                r = requests.get(url, headers=headers, timeout=3)
                if r.status_code == 200:
                    ultimo_resultado_set = set([int(d) for d in r.json()['dezenas']])
            except:
                pass

        # 4. Cálculos
        variaveis = list(pool_20 - fixas)
        jogos_candidatos = []
        
        if not ultimo_resultado_set:
            ultimo_resultado_set = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15} # Dummy

        for combinacao in itertools.combinations(variaveis, 5):
            jogo_atual = fixas.union(combinacao)
            repetidas = len(jogo_atual.intersection(ultimo_resultado_set))
            primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
            qtd_primos = len(jogo_atual.intersection(primos_set))
            jogos_candidatos.append({'numeros': sorted(list(jogo_atual)), 'repetidas': repetidas, 'primos': qtd_primos})

        melhores_jogos = [j for j in jogos_candidatos if j['repetidas'] == 9]
        if len(melhores_jogos) < 4:
            reserva = [j for j in jogos_candidatos if j['repetidas'] in [8, 10]]
            reserva.sort(key=lambda x: abs(x['primos'] - 5))
            melhores_jogos.extend(reserva)
        
        jogos_finais = melhores_jogos[:5]

        # 5. Exibição dos Jogos
        if not jogos_finais:
            lbl_status.value = "Nenhum jogo encontrado com esses critérios."
            lbl_status.color = "orange"
        else:
            dados_csv = []
            str_20 = ";".join([f"{n:02d}" for n in sorted(list(pool_20))])
            str_ult = ";".join([f"{n:02d}" for n in sorted(list(ultimo_resultado_set))])
            dados_csv.append({"Tipo": "Matriz", "Dezenas": str_20, "Info": info_estrategia})
            dados_csv.append({"Tipo": "Base", "Dezenas": str_ult, "Info": txt_concurso_base.value})

            for i, jogo in enumerate(jogos_finais):
                str_visual = " - ".join([f"{n:02d}" for n in jogo['numeros']])
                str_csv = ";".join([f"{n:02d}" for n in jogo['numeros']])
                
                dados_csv.append({"Tipo": f"Jogo {i+1}", "Dezenas": str_csv, "Info": f"R:{jogo['repetidas']}"})
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {i+1}", weight="bold"),
                        ft.Text(f"{str_visual}", size=20, color="blue"),
                        ft.Text(f"R:{jogo['repetidas']} | P:{jogo['primos']}", size=12)
                    ]),
                    padding=10, bgcolor="blue50", border_radius=10, margin=5
                )
                lista_resultados.controls.append(card)

            # Salvar
            nome_arq = f"Loto_{txt_concurso_alvo.value}.csv"
            caminho_final = os.path.join(caminho_pasta, nome_arq)
            try:
                df = pd.DataFrame(dados_csv)
                df.to_csv(caminho_final, index=False, sep=';', encoding='utf-8-sig')
                if "ERRO" not in lbl_status.value:
                    lbl_status.value = f"Sucesso! Salvo em Downloads."
                    lbl_status.color = "green"
            except Exception as e:
                lbl_status.value = f"Erro ao salvar: {e}"
        
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
