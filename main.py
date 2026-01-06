import flet as ft
import itertools
import csv
import sys

# Variável global para dados
dados_para_salvar = []

def main(page: ft.Page):
    global dados_para_salvar
    
    # Configuração da Janela
    page.title = "Lotofácil Offline"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"
    page.window_width = 400

    # --- SISTEMA DE SALVAR ARQUIVO (Nativo) ---
    def salvar_arquivo_final(e: ft.FilePickerResultEvent):
        global dados_para_salvar
        if e.path:
            try:
                # Cria o CSV usando biblioteca padrão do Python (Super Leve)
                with open(e.path, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["Descricao", "Dezenas", "Detalhes"], delimiter=';')
                    writer.writeheader()
                    writer.writerows(dados_para_salvar)
                
                lbl_status.value = "SUCESSO! Arquivo salvo."
                lbl_status.color = "green"
                page.open(ft.SnackBar(content=ft.Text("Arquivo salvo com sucesso!")))
                
            except Exception as erro:
                lbl_status.value = f"Erro ao gravar: {erro}"
                lbl_status.color = "red"
        else:
            lbl_status.value = "Salvamento cancelado."
        page.update()

    file_picker = ft.FilePicker(on_result=salvar_arquivo_final)
    page.overlay.append(file_picker)

    # --- UI ---
    titulo = ft.Text("Gerador Lotofácil (Offline)", size=24, weight="bold", color="blue")
    subtitulo = ft.Text("Matriz Estatística Fixa", size=14, color="grey")

    # Inputs manuais (já que não temos internet)
    txt_concurso_alvo = ft.TextField(label="Concurso Futuro", width=150, text_align="center", keyboard_type="number")
    txt_ultimo_resultado = ft.TextField(
        label="Digite o Último Resultado (separado por espaço)", 
        multiline=True, 
        min_lines=2, 
        hint_text="Ex: 01 02 03 04 05..."
    )
    
    lbl_status = ft.Text("Pronto para gerar.", color="grey", weight="bold")
    lista_res = ft.ListView(expand=1, spacing=10, padding=20)

    # --- LÓGICA MATEMÁTICA PURA ---
    def processar(e):
        global dados_para_salvar
        dados_para_salvar = []
        lista_res.controls.clear()
        
        lbl_status.value = "Calculando..."
        page.update()

        # 1. Validar Último Resultado
        try:
            texto_numeros = txt_ultimo_resultado.value.replace(",", " ").replace("-", " ")
            lista_str = texto_numeros.split()
            ultimo_resultado_set = set(map(int, lista_str))
            
            if len(ultimo_resultado_set) < 15:
                lbl_status.value = f"Erro: Digite 15 números (Você digitou {len(ultimo_resultado_set)})"
                lbl_status.color = "red"
                page.update()
                return
        except:
            lbl_status.value = "Erro: Digite apenas números no resultado."
            lbl_status.color = "red"
            page.update()
            return

        # 2. Matriz Fixa (Os 20 de Ouro)
        pool_20 = {1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 24, 25}
        fixas = {1, 3, 5, 10, 11, 13, 20, 23, 24, 25}
        variaveis = list(pool_20 - fixas)

        # 3. Gerar Combinações
        jogos_filtrados = []
        
        for comb in itertools.combinations(variaveis, 5):
            jogo = fixas.union(comb)
            # Filtro: Repetidas do anterior
            repetidas = len(jogo.intersection(ultimo_resultado_set))
            
            # Filtro Matemático Rigoroso (Apenas 9 repetidas)
            if repetidas == 9:
                jogos_filtrados.append(sorted(list(jogo)))

        # Se não achou com 9, tenta com 8 ou 10 (Plano B)
        if not jogos_filtrados:
            for comb in itertools.combinations(variaveis, 5):
                jogo = fixas.union(comb)
                repetidas = len(jogo.intersection(ultimo_resultado_set))
                if repetidas in [8, 10]:
                    jogos_filtrados.append(sorted(list(jogo)))

        # Pega os Top 5
        finais = jogos_filtrados[:5]

        # 4. Exibir e Preparar Salvar
        if not finais:
            lbl_status.value = "Nenhum jogo compatível com a matriz."
            lbl_status.color = "orange"
        else:
            # Salva o resultado base
            str_base = " - ".join([f"{n:02d}" for n in sorted(list(ultimo_resultado_set))])
            dados_para_salvar.append({"Descricao": "Base Usada", "Dezenas": str_base, "Detalhes": "Manual"})
            
            lista_res.controls.append(
                ft.Container(content=ft.Text(f"Base: {str_base}", color="orange"), padding=5)
            )

            for i, j in enumerate(finais):
                str_num = ";".join([f"{n:02d}" for n in j])
                str_vis = " - ".join([f"{n:02d}" for n in j])
                
                # Dados CSV
                dados_para_salvar.append({"Descricao": f"Jogo {i+1}", "Dezenas": str_num, "Detalhes": "Gerado"})
                
                # Visual Tela
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {i+1}", weight="bold"),
                        ft.Text(str_vis, size=20, color="blue")
                    ]),
                    padding=10, bgcolor="blue50", border_radius=8
                )
                lista_res.controls.append(card)

            lbl_status.value = "Sucesso! Clique abaixo para salvar."
            lbl_status.color = "green"
            
            # Botão de Salvar aparece agora
            file_picker.save_file(file_name=f"Loto_{txt_concurso_alvo.value}.csv", allowed_extensions=["csv"])

        page.update()

    def sair(e):
        sys.exit()

    # Botões
    btn_gerar = ft.FilledButton("GERAR E SALVAR", on_click=processar, width=200, height=50)
    btn_sair = ft.FilledButton("SAIR", on_click=sair, style=ft.ButtonStyle(bgcolor="red"), width=100)

    page.add(
        ft.Column([
            titulo, subtitulo,
            txt_concurso_alvo,
            txt_ultimo_resultado,
            ft.Divider(),
            ft.Row([btn_sair, btn_gerar], alignment="center"),
            lbl_status,
            lista_res
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main)
