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
    
    # Linha 1: Concursos
    txt_concurso_alvo = ft.TextField(
        label="Próximo Concurso", 
        width=150,
        text_align=ft.TextAlign.CENTER,
        hint_text="Ex: 3200"
    )

    txt_concurso_base = ft.TextField(
        label="Último Sorteado", 
        width=150,
        text_align=ft.TextAlign.CENTER,
        hint_text="Ex: 3199"
    )

    # Linha 2: Configuração da Análise Automática
    txt_qtd_analise = ft.TextField(
        label="Analisar últimos X concursos?",
        value="10",  # Padrão: analisa os últimos 10
        width=250,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    # Checkbox para ativar/desativar a busca online
    chk_usar_online = ft.Checkbox(label="Buscar estatísticas online (Automático)", value=True)

    lbl_status = ft.Text("Pronto.", color="grey")
    barra_progresso = ft.ProgressBar(width=400, color="blue", bgcolor="#eeeeee", visible=False)
    
    lista_resultados = ft.ListView(expand=1, spacing=10, padding=20)

    # --- FUNÇÕES DO SISTEMA ---

    def fechar_app(e):
        """Força o fechamento do App no Android"""
        sys.exit()

    def limpar_filtros(e=None):
        txt_concurso_alvo.value = ""
        txt_concurso_base.value = ""
        lbl_status.value = "Limpo."
        lbl_status.color = "grey"
        lista_resultados.controls.clear()
        page.update()

    def buscar_estatisticas_online(ultimo_concurso, qtd_analise):
        """
        Busca os resultados na API e retorna as melhores dezenas.
        """
        numeros_contados = []
        try:
            base = int(ultimo_concurso)
            qtd = int(qtd_analise)
            
            sucesso = 0
            
            # Busca resultados um por um
            for i in range(qtd):
                concurso_atual = base - i
                # API Pública da Caixa
                url = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{concurso_atual}"
                
                try:
                    response = requests.get(url, timeout=3) # Timeout curto para não travar muito
                    if response.status_code == 200:
                        dados = response.json()
                        dezenas = [int(d) for d in dados['dezenas']]
                        numeros_contados.extend(dezenas)
                        sucesso += 1
                except:
                    continue # Se falhar um, tenta o próximo
                
            if sucesso < 3:
                return None, None, "Falha: Poucos dados obtidos online."

            # Estatística Pura: Quem saiu mais vezes nesse período?
            frequencia = Counter(numeros_contados)
            
            # Pega os 20 mais frequentes
            top_20_com_freq = frequencia.most_common(20)
            top_20 = sorted([num for num, freq in top_20_com_freq])
            
            # Pega os 10 mais frequentes (para serem as Fixas)
            top_10_com_freq = frequencia.most_common(10)
            fixas = sorted([num for num, freq in top_10_com_freq])
            
            msg = f"Baseado nos últimos {sucesso} concursos."
            return set(top_20), set(fixas), msg

        except Exception as e:
            return None, None, f"Erro Online: {e}"

    # --- LÓGICA PRINCIPAL ---
    def gerar_jogos(e):
        # 1. Início do processamento
        lista_resultados.controls.clear()
        btn_gerar.disabled = True
        barra_progresso.visible = True
        lbl_status.value = "Conectando à internet..."
        lbl_status.color = "blue"
        page.update()

        # 2. Caminho de salvamento
        try:
            if page.platform == ft.PagePlatform.ANDROID:
                caminho_pasta = "/storage/emulated/0/Download"
            else:
                caminho_pasta = r"D:\Phyton\Lotofacil"
                
            if page.platform != ft.PagePlatform.ANDROID and not os.path.exists(caminho_pasta):
                os.makedirs(caminho_pasta)
        except Exception as erro:
            lbl_status.value = f"Erro pasta: {erro}"
            barra_progresso.visible = False
            btn_gerar.disabled = False
            page.update()
            return

        # 3. Validação dos Campos
        concurso_alvo = txt_concurso_alvo.value.strip()
        concurso_base = txt_concurso_base.value.strip()
        
        if not concurso_alvo or not concurso_base:
            lbl_status.value = "Preencha os números dos concursos."
            lbl_status.color = "red"
            barra_progresso.visible = False
            btn_gerar.disabled = False
            page.update()
            return

        # 4. INTELIGÊNCIA (Busca Online ou Padrão)
        
        pool_20 = set()
        fixas = set()
        info_estrategia = "Manual"
        ultimo_resultado_set = set()

        if chk_usar_online.value:
            lbl_status.value = "Baixando resultados e calculando estatísticas..."
            page.update()
            
            p20, fx, msg = buscar_estatisticas_online(concurso_base, txt_qtd_analise.value)
            
            if p20:
                pool_20 = p20
                fixas = fx
                info_estrategia = f"IA Online ({msg})"
                lbl_status.value = "Análise concluída! Gerando jogos..."
            else:
                lbl_status.value = f"Sem conexão ({msg}). Usando padrão."
                # Matriz de Emergência (números historicamente fortes)
                pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
                fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
                info_estrategia = "Padrão (Falha Conexão)"
        else:
            # Matriz Padrão Fixa
            pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
            fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
            info_estrategia = "Manual Offline"

        # Tenta buscar o último resultado exato para filtrar repetidas
        try:
            if chk_usar_online.value:
                 url_base = f"https://loteriascaixa-api.herokuapp.com/api/lotofacil/{concurso_base}"
                 resp = requests.get(url_base, timeout=3)
                 if resp.status_code == 200:
                     ultimo_resultado_set = set([int(d) for d in resp.json()['dezenas']])
        except:
            pass 

        # 5. MOTOR MATEMÁTICO
        variaveis = list(pool_20 - fixas)
        jogos_candidatos = []

        # Se falhou em pegar o último, cria um dummy para não travar o loop
        if not ultimo_resultado_set:
            ultimo_resultado_set = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15} 
            info_estrategia += " (Sem filtro repetidas)"

        for combinacao in itertools.combinations(variaveis, 5):
            jogo_atual = fixas.union(combinacao)
            repetidas = len(jogo_atual.intersection(ultimo_resultado_set))
            primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
            qtd_primos = len(jogo_atual.intersection(primos_set))

            jogos_candidatos.append({
                'numeros': sorted(list(jogo_atual)),
                'repetidas': repetidas,
                'primos': qtd_primos
            })

        # Filtros (Repetidas = 9)
        melhores_jogos = [j for j in jogos_candidatos if j['repetidas'] == 9]
        if len(melhores_jogos) < 4:
            reserva = [j for j in jogos_candidatos if j['repetidas'] in [8, 10]]
            reserva.sort(key=lambda x: abs(x['primos'] - 5))
            melhores_jogos.extend(reserva)
        
        jogos_finais = melhores_jogos[:5]

        # 6. RESULTADOS E CSV
        if not jogos_finais:
            lbl_status.value = "Nenhum jogo atende aos critérios."
            lbl_status.color = "orange"
        else:
            dados_csv = []
            
            str_20 = ";".join([f"{n:02d}" for n in sorted(list(pool_20))])
            str_ult = ";".join([f"{n:02d}" for n in sorted(list(ultimo_resultado_set))])
            
            dados_csv.append({"Tipo": "Matriz (Top 20)", "Dezenas": str_20, "Info": info_estrategia})
            dados_csv.append({"Tipo": f"Base ({concurso_base})", "Dezenas": str_ult, "Info": "Referência"})

            for i, jogo in enumerate(jogos_finais):
                str_jogo = ";".join([f"{n:02d}" for n in jogo['numeros']])
                str_visual = " - ".join([f"{n:02d}" for n in jogo['numeros']])
                
                dados_csv.append({
                    "Tipo": f"Jogo {i+1}", 
                    "Dezenas": str_jogo, 
                    "Info": f"R:{jogo['repetidas']} | P:{jogo['primos']}"
                })

                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {i+1}", weight="bold", size=16),
                        ft.Text(f"{str_visual}", size=20, color="blue"),
                        ft.Text(f"R:{jogo['repetidas']} | P:{jogo['primos']}", size=12, color="grey")
                    ]),
                    padding=10,
                    bgcolor="blue50",
                    border_radius=10,
                    margin=5
                )
                lista_resultados.controls.append(card)

            # Salvar
            nome_arquivo = f"LotoOnline_{concurso_alvo}.csv"
            caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
            try:
                df = pd.DataFrame(dados_csv)
                df.to_csv(caminho_completo, index=False, sep=';', encoding='utf-8-sig')
                lbl_status.value = f"Sucesso! Salvo em Downloads."
                lbl_status.color = "green"
            except Exception as e:
                lbl_status.value = f"Erro ao salvar: {e}"
                lbl_status.color = "red"

        barra_progresso.visible = False
        btn_gerar.disabled = False
        page.update()

    # --- BOTÕES ---
    btn_gerar = ft.FilledButton("GERAR ONLINE", width=140, height=50, on_click=gerar_jogos)
    
    btn_limpar = ft.FilledButton("LIMPAR", width=100, height=50, 
                                 style=ft.ButtonStyle(bgcolor="grey"), 
                                 on_click=limpar_filtros)
    
    # Botão SAIR usando sys.exit()
    btn_sair = ft.FilledButton("SAIR", width=80, height=50, 
                               style=ft.ButtonStyle(bgcolor="red"), 
                               on_click=fechar_app)

    # --- LAYOUT ---
    page.add(
        ft.Column(
            [
                titulo,
                ft.Row([txt_concurso_alvo, txt_concurso_base], alignment=ft.MainAxisAlignment.CENTER),
                txt_qtd_analise,
                chk_usar_online,
                ft.Divider(),
                ft.Row([btn_sair, btn_limpar, btn_gerar], alignment=ft.MainAxisAlignment.CENTER),
                barra_progresso,
                lbl_status,
                lista_resultados
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
