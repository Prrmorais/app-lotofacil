import flet as ft
import itertools
import pandas as pd
import os

def main(page: ft.Page):
    # --- CONFIGURAÇÕES VISUAIS ---
    page.title = "Gerador Lotofácil Pro"
    page.window_width = 450
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"
    
    # --- LÓGICA (BACK-END) ---
    def gerar_jogos(e):
        # 1. Feedback visual
        lista_resultados.controls.clear()
        lbl_status.value = "Processando..."
        lbl_status.color = "blue" # Usando string direta
        page.update()

        # 2. Pasta
        caminho_pasta = r"D:\Phyton\Lotofacil"
        if not os.path.exists(caminho_pasta):
            try:
                os.makedirs(caminho_pasta)
            except Exception as erro:
                lbl_status.value = f"Erro pasta: {erro}"
                lbl_status.color = "red"
                page.update()
                return

        # 3. Inputs
        concurso = txt_concurso.value.strip()
        entrada_numeros = txt_resultado.value
        estrategia = dd_estrategia.value

        if not concurso:
            lbl_status.value = "Digite o concurso."
            lbl_status.color = "red"
            page.update()
            return

        # 4. Estratégia
        if estrategia == "ia":
            pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
            fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
            nome_est = "IA (Estatística)"
        else:
            pool_20 = {1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 25}
            fixas = {1, 3, 5, 10, 12, 13, 19, 20, 23, 25}
            nome_est = "Pessoais"

        # 5. Processamento
        try:
            numeros_limpos = entrada_numeros.replace(',', ' ').split()
            ultimo_resultado = set(map(int, numeros_limpos))
            if len(ultimo_resultado) < 15:
                lbl_status.value = f"Erro: Tem apenas {len(ultimo_resultado)} números."
                lbl_status.color = "red"
                page.update()
                return
        except ValueError:
            lbl_status.value = "Erro: Digite apenas números."
            lbl_status.color = "red"
            page.update()
            return

        # 6. Motor Matemático
        variaveis = list(pool_20 - fixas)
        jogos_candidatos = []

        for combinacao in itertools.combinations(variaveis, 5):
            jogo_atual = fixas.union(combinacao)
            repetidas = len(jogo_atual.intersection(ultimo_resultado))
            primos_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}
            qtd_primos = len(jogo_atual.intersection(primos_set))

            jogos_candidatos.append({
                'numeros': sorted(list(jogo_atual)),
                'repetidas': repetidas,
                'primos': qtd_primos
            })

        # 7. Filtros
        melhores_jogos = [j for j in jogos_candidatos if j['repetidas'] == 9]
        if len(melhores_jogos) < 4:
            reserva = [j for j in jogos_candidatos if j['repetidas'] in [8, 10]]
            reserva.sort(key=lambda x: abs(x['primos'] - 5))
            melhores_jogos.extend(reserva)
        
        jogos_finais = melhores_jogos[:4]

        # 8. Resultados
        if not jogos_finais:
            lbl_status.value = "Nenhum jogo encontrado."
            lbl_status.color = "orange"
        else:
            dados_csv = []
            
            str_20 = ";".join([f"{n:02d}" for n in sorted(list(pool_20))])
            str_ult = ";".join([f"{n:02d}" for n in sorted(list(ultimo_resultado))])
            
            dados_csv.append({"Descrição": "Matriz", "Dezenas": str_20, "Info": nome_est})
            dados_csv.append({"Descrição": "Ref Anterior", "Dezenas": str_ult, "Info": "Base"})

            for i, jogo in enumerate(jogos_finais):
                str_jogo = ";".join([f"{n:02d}" for n in jogo['numeros']])
                str_visual = " - ".join([f"{n:02d}" for n in jogo['numeros']])
                
                dados_csv.append({
                    "Descrição": f"Cartão {i+1}", 
                    "Dezenas": str_jogo, 
                    "Info": f"R:{jogo['repetidas']} | P:{jogo['primos']}"
                })

                # Card Visual (CORREÇÃO AQUI: bgcolor="blue50")
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Cartão {i+1}", weight="bold", size=16),
                        ft.Text(f"{str_visual}", size=20, color="blue"),
                        ft.Text(f"R:{jogo['repetidas']} | P:{jogo['primos']}", size=12, color="grey")
                    ]),
                    padding=10,
                    bgcolor="blue50", # String direta, funciona sempre
                    border_radius=10,
                    margin=5
                )
                lista_resultados.controls.append(card)

            # Salvar
            nome_arquivo = f"jogos_lotofacil_{concurso}.csv"
            caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
            try:
                df = pd.DataFrame(dados_csv)
                df.to_csv(caminho_completo, index=False, sep=';', encoding='utf-8-sig')
                lbl_status.value = f"Sucesso! Arquivo: {nome_arquivo}"
                lbl_status.color = "green"
            except Exception as e:
                lbl_status.value = f"Erro ao salvar: {e}"
                lbl_status.color = "red"

        page.update()

    # --- ELEMENTOS DA TELA ---
    
    titulo = ft.Text("Gerador Lotofácil", size=30, weight="bold", color="blue")
    
    txt_concurso = ft.TextField(label="Concurso (ex: 3200)", width=200)
    
    dd_estrategia = ft.Dropdown(
        width=400,
        label="Estratégia",
        value="ia",
        options=[
            ft.dropdown.Option("ia", "IA (Estatística)"),
            ft.dropdown.Option("pessoal", "Meus Números"),
        ],
    )

    txt_resultado = ft.TextField(
        label="Último Resultado (15 números)",
        multiline=True,
        min_lines=2,
        hint_text="Ex: 1 2 3 4 5..."
    )

    # Botão Simplificado
    btn_gerar = ft.FilledButton(
        content=ft.Text("GERAR JOGOS"),
        width=200,
        height=50,
        on_click=gerar_jogos
    )

    lbl_status = ft.Text("Aguardando...", color="grey")
    lista_resultados = ft.ListView(expand=1, spacing=10, padding=20)

    page.add(
        ft.Column(
            [
                titulo,
                txt_concurso,
                dd_estrategia,
                txt_resultado,
                ft.Divider(),
                ft.Row([btn_gerar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                lbl_status,
                lista_resultados
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

# Inicialização
if __name__ == "__main__":
    ft.app(target=main)